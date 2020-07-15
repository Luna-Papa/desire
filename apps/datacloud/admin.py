from django.contrib import admin
from .models import ChannelInfo, ChkInfo, SyncTaskInfo, PushTaskInfo, ScriptConfig
from django.db.models import Max, Count

# Register your models here.


@admin.register(ChannelInfo)
class ChannelInfoAdmin(admin.ModelAdmin):
    list_display = ('sys_name', 'chn_name', 'db_name', 'address', 'chn_start_time', 'created_time', 'sync_flag')
    fields = ('sys_name', 'chn_name', 'db_name', 'address', 'port', 'code_page', 'username', 'password', 'chn_start_time')

    def save_model(self, request, obj, form, change):
        obj.sync_flag = False
        if not change:
            # 自动生成数据源编号，每次递增100000
            channel_count = ChannelInfo.objects.count()
            if channel_count:
                obj.chn_id = (channel_count + 1) * 100000
            else:
                obj.chn_id = 100000
            # obj.chn_finish_id = obj.chn_id + 40000
            obj.chn_backup_id = obj.chn_id + 50000
            obj.new_record_flag = True
        return super(ChannelInfoAdmin, self).save_model(request, obj, form, change)


@admin.register(ChkInfo)
class ChkInfoAdmin(admin.ModelAdmin):
    list_display = ('db_name', 'chk_seq', 'chk_name', 'date_type', 'val_flag', 'created_time', 'sync_flag')
    fields = ('db_name', 'chk_name', 'chk_condition', 'chk_valid_condition', 'date_type', 'memo', 'val_flag')

    def save_model(self, request, obj, form, change):
        obj.sync_flag = False
        if not change:
            chk_info = ChkInfo.objects.filter(db_name=obj.db_name)
            if chk_info:
                db_name_count = chk_info.count()
                obj.chk_seq = db_name_count + 1
            else:
                obj.chk_seq = 1
            chn_id = ChannelInfo.objects.get(db_name=obj.db_name).chn_id
            obj.chk_id = chn_id + obj.chk_seq + 10000  # 检测编号规则是110001、110002
            obj.chk_done_id = chn_id + obj.chk_seq + 40000  # 渠道检测完成编号规则是140001、140002
            obj.new_record_flag = True
        return super(ChkInfoAdmin, self).save_model(request, obj, form, change)


@admin.register(SyncTaskInfo)
class SyncTaskInfoAdmin(admin.ModelAdmin):
    list_display = ('db_name', 'chk_name', 'tab_name', 'exp_method', 'zl_info', 'outfile_type',
                    'backup_flag', 'his_flag', 'val_flag')
    fields = ('db_name', 'chk_name', 'tab_name', 'exp_method', 'zl_info', 'zl_col', 'ftp_file',
              'outfile_type', 'date_type', 'out_path', 'load_method', 'load_tab_tmp',
              'load_tab_mir', 'month_flag', 'backup_flag', 'his_flag')
    list_editable = ('val_flag', 'his_flag', 'backup_flag')

    def save_model(self, request, obj, form, change):
        obj.sync_flag = False
        chn_id = ChannelInfo.objects.get(db_name=obj.db_name).chn_id
        if obj.out_path.endswith('/'):
            obj.out_path = obj.out_path[0:-1]
        if not change:
            task_info = SyncTaskInfo.objects.filter(db_name=obj.db_name)
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
            return self.readonly_fields + ('chk_name', 'db_name', )
        return self.readonly_fields


@admin.register(PushTaskInfo)
class PushTaskInfoAdmin(admin.ModelAdmin):
    list_display = ('db_name', 'source_tab_name', 'push_tab_name', 'file_type', 'code_page', 'path', 'val_flag')
    fields = ('source_tab_name', 'push_tab_name', 'path', 'file_type', 'code_page', 'separator', 'delimiter', 'val_flag')

    def save_model(self, request, obj, form, change):
        obj.sync_flag = False
        obj.db_name = SyncTaskInfo.objects.filter(tab_name=obj.source_tab_name)[0].db_name
        chn_id = ChannelInfo.objects.get(db_name=obj.db_name).chn_id
        if not change:
            task_info = PushTaskInfo.objects.filter(db_name=obj.db_name)
            if task_info:
                task_count = task_info.count()
                obj.push_id = chn_id + 60000 + task_count + 1
            else:
                obj.push_id = chn_id + 60001
            obj.new_record_flag = True
        return super(PushTaskInfoAdmin, self).save_model(request, obj, form, change)


@admin.register(ScriptConfig)
class ScriptConfigAdmin(admin.ModelAdmin):
    list_display = ('type', 'script', 'parameter')
    fields = ('type', 'script', 'parameter')
