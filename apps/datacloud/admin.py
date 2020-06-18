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
            max_chn_id = ChannelInfo.objects.all().aggregate(Max('chn_id'))['chn_id__max']
            if max_chn_id:
                obj.chn_id = max_chn_id + 100000
        return super(ChannelInfoAdmin, self).save_model(request, obj, form, change)


@admin.register(ChkInfo)
class ChkInfoAdmin(admin.ModelAdmin):
    list_display = ('db_name', 'chk_seq', 'chk_name', 'date_type', 'val_flag', 'created_time', 'sync_flag')
    fields = ('db_name', 'chk_name', 'chk_condition', 'chk_valid_condition', 'date_type', 'memo', 'val_flag')

    def save_model(self, request, obj, form, change):
        obj.sync_flag = False
        chk_info = ChkInfo.objects.filter(db_name=obj.db_name)
        if chk_info:
            db_name_count = chk_info.count()
            obj.chk_seq = db_name_count + 1
        else:
            obj.chk_seq = 1
        chn_id = ChannelInfo.objects.get(db_name=obj.db_name).chn_id
        obj.chk_id = chn_id + obj.chk_seq
        return super(ChkInfoAdmin, self).save_model(request, obj, form, change)
