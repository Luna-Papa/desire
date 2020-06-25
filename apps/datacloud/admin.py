from django.contrib import admin
from .models import ChannelInfo, ChkInfo, SyncTaskInfo, PushTaskInfo
from django.db.models import Max, Count

# Register your models here.


@admin.register(ChannelInfo)
class ChannelInfoAdmin(admin.ModelAdmin):
    list_display = ('sys_name', 'chn_name', 'db_name', 'address', 'created_time', 'sync_flag')
    fields = ('sys_name', 'chn_name', 'db_name', 'address', 'port', 'code_page', 'username', 'password')

    def save_model(self, request, obj, form, change):
        obj.sync_flag = False
        if not change:
            # 自动生成数据源编号，每次递增100000
            channel_count = ChannelInfo.objects.count()
            if channel_count:
                obj.chn_id = (channel_count + 1) * 100000
            else:
                obj.chn_id = 100000
            # max_chn_id = ChannelInfo.objects.all().aggregate(Max('chn_id'))['chn_id__max']
            # if max_chn_id:
            #     obj.chn_id = max_chn_id + 100000
            obj.chn_finish_id = obj.chn_id + 40000
            obj.chn_backup_id = obj.chn_id + 50000
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
        return super(ChkInfoAdmin, self).save_model(request, obj, form, change)

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == 'chk_name':
    #         kwargs['queryset'] = ChkInfo.objects.filter(db_name=)
    #     return super(ChkInfoAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(SyncTaskInfo)
class SyncTaskInfoAdmin(admin.ModelAdmin):
    list_display = ('db_name', 'chk_name', 'tab_name', 'exp_method', 'zl_info', 'outfile_type',
                    'backup_flag', 'his_flag', 'val_flag')
    fields = ('db_name', 'chk_name', 'tab_name', 'exp_method', 'zl_info', 'zl_col', 'ftp_file',
              'outfile_type', 'date_type', 'out_path', 'load_method', 'load_tab_tmp',
              'load_tab_mir', 'month_flag', 'backup_flag', 'his_flag', 'val_flag')

    def save_model(self, request, obj, form, change):
        obj.sync_flag = False
        chn_id = ChannelInfo.objects.get(db_name=obj.db_name).chn_id
        if not change:
            task_info = SyncTaskInfo.objects.filter(db_name=obj.db_name)
            if task_info:
                task_count = task_info.count()
                obj.sync_id = chn_id + 20000 + task_count + 1
                obj.load_id = chn_id + 30000 + task_count + 1
            else:
                obj.sync_id = chn_id + 20001
                obj.load_id = chn_id + 30001
        return super(SyncTaskInfoAdmin, self).save_model(request, obj, form, change)


@admin.register(PushTaskInfo)
class PushTaskInfoAdmin(admin.ModelAdmin):
    list_display = ('db_name', 'tab_name', 'file_type', 'code_page', 'path', 'val_flag')
    fields = ('db_name', 'tab_name', 'path', 'file_type', 'code_page', 'separator', 'delimiter', 'val_flag')

    def save_model(self, request, obj, form, change):
        obj.sync_flag = False
        chn_id = ChannelInfo.objects.get(db_name=obj.db_name).chn_id
        if not change:
            task_info = PushTaskInfo.objects.filter(db_name=obj.db_name)
            if task_info:
                task_count = task_info.count()
                obj.push_id = chn_id + 60000 + task_count + 1
            else:
                obj.push_id = chn_id + 60001
        return super(PushTaskInfoAdmin, self).save_model(request, obj, form, change)
