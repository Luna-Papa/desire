from django.contrib import admin
from .models import ChannelInfo, ChkInfo, SyncTaskInfo, PushTaskInfo, ScriptConfig, SmsSenderInfo
from .forms import SyncTaskInfoAdminForm
from import_export.admin import ImportExportModelAdmin

# Register your models here.


admin.site.site_header = '数据云管理后台'
admin.site.site_title = '数据云'


@admin.register(ChannelInfo)
class ChannelInfoAdmin(ImportExportModelAdmin):
    list_display = ('sys_name', 'chn_name', 'db_name', 'address', 'chn_start_time',
                    'created_time', 'sync_flag')
    fields = ('sys_name', 'chn_name', 'db_name', 'address', 'port', 'code_page',
              'username', 'password', 'chn_start_time')
    search_fields = ['chn_name', 'db_name', 'sys_name']

    def save_model(self, request, obj, form, change):
        obj.sync_flag = False
        obj.sys_name = obj.sys_name.strip().upper()
        obj.chn_name = obj.chn_name.strip()
        obj.db_name = obj.db_name.strip()
        if not change:
            # 自动生成数据源编号，每次递增100000
            channel_count = ChannelInfo.objects.count()
            if channel_count:
                obj.chn_id = (channel_count + 1) * 100000
            else:
                obj.chn_id = 100000
            # obj.chn_finish_id = obj.chn_id + 40000
            obj.chn_backup_id = obj.chn_id + 50001
            obj.new_record_flag = True
        return super(ChannelInfoAdmin, self).save_model(request, obj, form, change)


@admin.register(ChkInfo)
class ChkInfoAdmin(ImportExportModelAdmin):
    list_display = ('chn_name', 'chk_seq', 'chk_name', 'date_type', 'val_flag', 'sync_flag')
    fields = ('chn_name', 'chk_name', 'chk_condition', 'chk_valid_condition', 'date_type', 'memo', 'val_flag')
    search_fields = ['chk_name']
    autocomplete_fields = ['chn_name']

    def save_model(self, request, obj, form, change):
        obj.sync_flag = False
        if not change:
            chk_info = ChkInfo.objects.filter(chn_name=obj.chn_name)
            if chk_info:
                db_name_count = chk_info.count()
                obj.chk_seq = db_name_count + 1
            else:
                obj.chk_seq = 1
            chn_id = ChannelInfo.objects.get(chn_name=obj.chn_name).chn_id
            obj.chk_id = chn_id + obj.chk_seq + 10000  # 检测编号规则是110001、110002
            obj.chk_done_id = chn_id + obj.chk_seq + 40000  # 渠道检测完成编号规则是140001、140002
            obj.new_record_flag = True
        return super(ChkInfoAdmin, self).save_model(request, obj, form, change)


@admin.register(SyncTaskInfo)
class SyncTaskInfoAdmin(ImportExportModelAdmin):
    form = SyncTaskInfoAdminForm
    list_display = ('chn_name', 'chk_name', 'tab_name', 'exp_method', 'zl_info',
                    # 'outfile_type', 'backup_flag', 'his_flag', 'his_frequency',
                    'val_flag', 'sync_flag')
    # change_form_template = 'admin/extra/record_change_form.html'
    fields = ('chk_name', 'tab_name', 'exp_method', 'zl_info', 'zl_col', 'ftp_file',
              'outfile_type', 'date_type', 'out_path', 'load_method',
              'month_flag', 'backup_flag', 'his_flag', 'his_frequency')
    autocomplete_fields = ['chk_name']
    search_fields = ['tab_name', 'chk_name']

    def save_model(self, request, obj, form, change):

        # 根据chk_name处理chn_name
        obj.chn_name = obj.chk_name.chn_name

        obj.sync_flag = False
        chn_id = ChannelInfo.objects.get(chn_name=obj.chn_name).chn_id

        # 处理表名：当源系统为ODS时，表名不处理；
        # 源系统为其它系统时将表名中的下划线去除
        obj.tab_name = obj.tab_name.strip().upper()
        tab_name = obj.tab_name.split('.', 1)[1]
        # 源系统为ODS时，表名要继续拆分
        ods_tab_name = ''  # ODS存储的实际表名
        ods_chn_name = ''  # ODS存储的表对应的渠道名
        if obj.chn_name.sys_name == 'ODS':
            ods_tab_name = tab_name.split('_')[-1]
            ods_chn_name = tab_name.split('_')[0]
            obj.load_tab_tmp = f"ARES.{ods_chn_name}_TMP_{ods_tab_name}"
            obj.load_tab_mir = f"ARES.{ods_chn_name}_MIR_{ods_tab_name}"
        else:
            obj.load_tab_tmp = f"ARES.{obj.chn_name.sys_name}_TMP_{tab_name.replace('_', '')}"
            obj.load_tab_mir = f"ARES.{obj.chn_name.sys_name}_MIR_{tab_name.replace('_', '')}"

            # 历史表表名的处理
            if obj.his_flag:
                if obj.chn_name.sys_name == 'ODS':
                    obj.his_tab = f"Demeter.{ods_chn_name}_HIS_{ods_tab_name}"
                else:
                    obj.his_tab = f"Demeter.{obj.chn_name.sys_name}_HIS_{tab_name.replace('_', '')}"
            else:
                obj.his_tab = ''

        # 处理路径，自动去除末尾的/
        if obj.out_path.endswith('/'):
            obj.out_path = obj.out_path[0:-1]

        # 当导出方式为ftp或cdc时，增量标识和增量检测字段置为空
        if obj.exp_method == 'ftp' or obj.exp_method == 'cdc':
            obj.zl_info = ''
            obj.zl_col = ''
        # 当导出方式为export或hpu时，ftp条件字段置为空
        elif obj.exp_method == 'export' or obj.exp_method == 'hpu':
            obj.ftp_file = ''
            # 当增量标识为全量时，增量同步字段置为空
            if obj.zl_info == 'Q':
                obj.zl_col = ''

        # 作业号的生成逻辑
        if not change:
            task_info = SyncTaskInfo.objects.filter(chn_name=obj.chn_name)
            if task_info:
                task_count = task_info.count()
                obj.sync_id = chn_id + 20000 + task_count + 1
                obj.load_id = chn_id + 30000 + task_count + 1
            else:
                obj.sync_id = chn_id + 20001
                obj.load_id = chn_id + 30001
            obj.new_record_flag = True
        return super(SyncTaskInfoAdmin, self).save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        # 修改对象时，源系统名和检测名称不可修改
        if obj:
            return self.readonly_fields + ('chk_name', 'db_name',)
        return self.readonly_fields


@admin.register(PushTaskInfo)
class PushTaskInfoAdmin(ImportExportModelAdmin):
    list_display = ('chn_name', 'push_tab_name', 'file_type',
                    'code_page', 'path', 'val_flag', 'sync_flag')
    fields = ('chn_name', 'source_tab_name', 'push_type', 'path', 'file_type', 'code_page',
              'separator', 'delimiter', 'val_flag')
    autocomplete_fields = ['source_tab_name']

    def save_model(self, request, obj, form, change):
        obj.sync_flag = False
        obj.chn_name = SyncTaskInfo.objects.filter(tab_name=obj.source_tab_name)[0].chn_name
        chn_id = ChannelInfo.objects.get(chn_name=obj.chn_name).chn_id
        if obj.push_type == 'TMP':
            obj.push_tab_name = obj.source_tab_name.load_tab_tmp
        elif obj.push_type == 'MIR':
            obj.push_tab_name = obj.source_tab_name.load_tab_mir

        # 当导出格式为ixf时，字段分隔符和字段限定符均置为空
        if obj.file_type == 'ixf':
            obj.separator = ''
            obj.delimiter = ''

        if not change:
            task_info = PushTaskInfo.objects.filter(chn_name=obj.chn_name)
            if task_info:
                task_count = task_info.count()
                obj.push_id = chn_id + 60000 + task_count + 1
            else:
                obj.push_id = chn_id + 60001
            obj.new_record_flag = True
        return super(PushTaskInfoAdmin, self).save_model(request, obj, form, change)


@admin.register(ScriptConfig)
class ScriptConfigAdmin(ImportExportModelAdmin):
    list_display = ('type', 'type_name', 'script', 'parameter')
    fields = ('type', 'type_name', 'script', 'parameter')


@admin.register(SmsSenderInfo)
class SmsSenderInfoAdmin(ImportExportModelAdmin):
    list_display = ('name', 'phone', 'val_flag', 'sync_flag')
    fields = ('name', 'phone', 'val_flag')
    list_editable = ('phone', 'val_flag')

    def save_model(self, request, obj, form, change):
        obj.sync_flag = False
        return super(SmsSenderInfoAdmin, self).save_model(request, obj, form, change)
