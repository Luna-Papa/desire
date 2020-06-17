from django.contrib import admin
from .models import ChannelInfo, ChkInfo, SyncTaskInfo, PushTaskInfo

# Register your models here.


@admin.register(ChannelInfo)
class ChannelInfoAdmin(admin.ModelAdmin):
    list_display = ('sys_name', 'chn_name', 'db_name', 'address', 'created_time', 'sync_flag')
    fields = ('sys_name', 'chn_name', 'db_name', 'address', 'port', 'code_page', 'username', 'password')

    def save_model(self, request, obj, form, change):
        obj.sync_flag = False
        return super(ChannelInfoAdmin, self).save_model(request, obj, form, change)
