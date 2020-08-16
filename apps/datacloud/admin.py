from django.contrib import admin
from .models import ChannelInfo, ChkInfo, SyncTaskInfo, PushTaskInfo, PushSysInfo, PushSysTabInfo, ScriptConfig, SmsSenderInfo, Test001
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
    list_filter = ('val_flag',)

    def save_model(self, request, obj, form, change):
        obj.sync_flag = False
        obj.sys_name = obj.sys_name.strip().upper()
        obj.chn_name = obj.chn_name.strip()
        obj.db_name = obj.db_name.strip()
        if not change:
            # 自动生成数据源编号，每次递增1000000
            channel_count = ChannelInfo.objects.count()
            if channel_count:
                obj.chn_id = (channel_count + 1) * 1000000
            else:
                obj.chn_id = 1000000
            # obj.chn_finish_id = obj.chn_id + 40000
            obj.chn_backup_id = obj.chn_id + 50001
            obj.new_record_flag = True
        return super(ChannelInfoAdmin, self).save_model(request, obj, form, change)

    def get_actions(self, request):
        # 禁用列表页删除按钮
        actions = super(ChannelInfoAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        # 禁用编辑页删除按钮
        return False

    def change_val_flag(self, request, queryset):
        queryset.update(val_flag=False)

    change_val_flag.short_description = '置为无效'
    change_val_flag.icon = 'el-icon-close'
    change_val_flag.type = 'danger'

    actions = ['change_val_flag']

    def db_catalog(self, request, queryset):
        pass

    db_catalog.short_description = '数据源编目'
    # db_catalog.icon = 'el-icon-close'
    # db_catalog.type = 'danger'


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
            obj.chk_id = chn_id + obj.chk_seq + 10000  # 检测编号规则是1010001、1010002
            obj.chk_done_id = chn_id + obj.chk_seq + 40000  # 渠道检测完成编号规则是1040001、1040002
            obj.new_record_flag = True
        return super(ChkInfoAdmin, self).save_model(request, obj, form, change)

    def get_actions(self, request):
        # 禁用列表页删除按钮
        actions = super(ChkInfoAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        # 禁用编辑页删除按钮
        return False

    def change_val_flag(self, request, queryset):
        queryset.update(val_flag=False)

    change_val_flag.short_description = '置为无效'
    change_val_flag.icon = 'el-icon-close'
    change_val_flag.type = 'danger'

    actions = ['change_val_flag']


@admin.register(SyncTaskInfo)
class SyncTaskInfoAdmin(ImportExportModelAdmin):
    form = SyncTaskInfoAdminForm
    list_display = ('chn_name', 'chk_name', 'tab_name', 'exp_method', 'zl_info',
                    # 'outfile_type', 'backup_flag', 'his_flag', 'his_frequency',
                    'val_flag', 'sync_flag')
    # fields = ('chk_name', 'tab_name', 'exp_method', 'zl_info', 'zl_col', 'ftp_file',
    #           'outfile_type', 'date_type', 'out_path', 'load_method',
    #           'month_flag', 'backup_flag', 'his_flag', 'his_frequency')
    radio_fields = {'zl_info': admin.HORIZONTAL, 'exp_method': admin.HORIZONTAL,
                    'outfile_type': admin.HORIZONTAL, 'load_method': admin.HORIZONTAL,
                    'his_frequency': admin.HORIZONTAL}
    fieldsets = [
        ('任务配置',
         {
             'fields':
                 ['chk_name', 'tab_name', 'outfile_type', 'exp_method', 'date_type', 'load_method', 'zl_info']
         }),
        ('任务条件',
         {
             'fields':
                 ['out_path', 'zl_col', 'ftp_file']
         }),
        ('储存配置',
         {
             'fields':
                 ['month_flag', 'backup_flag', 'his_flag', 'his_frequency']
         })
    ]
    autocomplete_fields = ['chk_name']
    search_fields = ['tab_name', 'chk_name']
    list_filter = ('chn_name', 'chk_name')

    change_form_template = 'admin/extra/SyncTaskInfo_change_form.html'

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

            # 历史表表名的处理: 历史表模式为Demeter
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

        # 当不选择入历史中心，历史频度字段置为空
        if not obj.his_flag:
            obj.his_his_frequency = ''

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

    def get_actions(self, request):
        # 禁用列表页删除按钮
        actions = super(SyncTaskInfoAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        # 禁用编辑页删除按钮
        return False

    def change_val_flag(self, request, queryset):
        queryset.update(val_flag=False)

    change_val_flag.short_description = '置为无效'
    change_val_flag.icon = 'el-icon-close'
    change_val_flag.type = 'danger'

    def table_full_sync(self, request, queryset):
        pass

    table_full_sync.short_description = '全量同步'
    # db_catalog.icon = 'el-icon-close'
    # db_catalog.type = 'danger'

    actions = ['change_val_flag']


@admin.register(PushTaskInfo)
class PushTaskInfoAdmin(ImportExportModelAdmin):

    list_display = ('chn_name', 'push_tab_name', 'file_type',
                    'code_page', 'path', 'val_flag', 'sync_flag')
    fields = ('chn_name', 'source_tab_name', 'push_type', 'path', 'file_type', 'code_page',
              'separator', 'delimiter', 'val_flag')
    autocomplete_fields = ['source_tab_name']
    radio_fields = {
        'push_type': admin.HORIZONTAL,
        'file_type': admin.HORIZONTAL,
        'code_page': admin.HORIZONTAL,
    }
    list_filter = ('chn_name',)
    search_fields = ('chn_name', 'source_tab_name', 'push_tab_id')

    change_form_template = 'admin/extra/PushTaskInfo_change_form.html'

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

        # 生成推送表唯一标识
        obj.push_tab_id = f'{obj.push_tab_name}_{obj.code_page}'
        if obj.separator:
            obj.push_tab_id += f'_{obj.separator}'
        if obj.delimiter:
            obj.push_tab_id += f'_{obj.delimiter}'
        obj.push_tab_id += f'.{obj.file_type}'

        if not change:
            task_info = PushTaskInfo.objects.filter(chn_name=obj.chn_name)
            if task_info:
                task_count = task_info.count()
                obj.push_id = chn_id + 60000 + task_count + 1
            else:
                obj.push_id = chn_id + 60001
            obj.new_record_flag = True
        return super(PushTaskInfoAdmin, self).save_model(request, obj, form, change)

    def get_actions(self, request):
        # 禁用列表页删除按钮
        actions = super(PushTaskInfoAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        # 禁用编辑页删除按钮
        return False

    def change_val_flag(self, request, queryset):
        queryset.update(val_flag=False)

    change_val_flag.short_description = '置为无效'
    change_val_flag.icon = 'el-icon-close'
    change_val_flag.type = 'danger'

    def table_full_push(self, request, queryset):
        pass

    table_full_push.short_description = '全量推送'
    # db_catalog.icon = 'el-icon-close'
    # db_catalog.type = 'danger'

    actions = ['change_val_flag']


@admin.register(ScriptConfig)
class ScriptConfigAdmin(ImportExportModelAdmin):
    list_display = ('type', 'type_name', 'script', 'parameter')
    fields = ('type', 'type_name', 'script', 'parameter')

    def get_actions(self, request):
        # 禁用列表页删除按钮
        actions = super(ScriptConfigAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        # 禁用编辑页删除按钮
        return False


@admin.register(SmsSenderInfo)
class SmsSenderInfoAdmin(ImportExportModelAdmin):
    list_display = ('name', 'phone', 'val_flag', 'sync_flag')
    fields = ('name', 'phone', 'val_flag')
    list_editable = ('phone', 'val_flag')

    def save_model(self, request, obj, form, change):
        obj.sync_flag = False
        return super(SmsSenderInfoAdmin, self).save_model(request, obj, form, change)


@admin.register(PushSysInfo)
class PushSysInfoAdmin(ImportExportModelAdmin):
    list_display = ('system_abbr', 'system_name', 'push_path', 'val_flag', 'sync_flag')
    fields = ('system_abbr', 'system_name', 'push_path', 'val_flag')
    search_fields = ('system_name', 'system_abbr')

    def save_model(self, request, obj, form, change):
        obj.system_abbr = obj.system_abbr.strip().upper()
        # 处理路径，自动去除末尾的/
        if obj.push_path.endswith('/'):
            obj.push_path = obj.push_path[0:-1]
        obj.sync_flag = False
        return super(PushSysInfoAdmin, self).save_model(request, obj, form, change)


@admin.register(PushSysTabInfo)
class PushSysTabInfoAdmin(ImportExportModelAdmin):
    list_display = ('system_name', 'tab_id', 'channel', 'val_flag', 'sync_flag')
    fields = ('system_name', 'tab_id', 'val_flag')
    autocomplete_fields = ['system_name', 'tab_id']

    def save_model(self, request, obj, form, change):
        # 生成推送表对应的源系统渠道号
        obj.channel = obj.tab_id.chn_name.sys_name

        obj.sync_flag = False
        return super(PushSysTabInfoAdmin, self).save_model(request, obj, form, change)


@admin.register(Test001)
class Test001Admin(ImportExportModelAdmin):
    list_display = ('chn_name', 'chk_name')
    fields = ('chn_name', 'chk_name')
    change_form_template = 'admin/extra/test.html'
