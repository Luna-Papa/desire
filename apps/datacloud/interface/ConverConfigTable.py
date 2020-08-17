import os
import pathlib
from django.core.wsgi import get_wsgi_application
from datetime import datetime
from datacloud.interface.tools import get_db_conn, get_sql_stmt

# 加载django项目环境参数
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "desire.settings")
application = get_wsgi_application()

from datacloud.models import ChannelInfo, ChkInfo, SyncTaskInfo, PushTaskInfo, \
    ScriptConfig, PushSysInfo, PushSysTabInfo, SyncTypes
from datacloud.interface.tools import get_db_conn, get_sql_stmt


#########################################################
# 根据前台配置表中的未同步记录：Sync_Flag值为False
# 关联更新后台配置表中的记录
# 更新方法：根据主键先删除再插入
#########################################################

def channel_info(sync_flag=False, curr=get_db_conn('ETL-Database')):
    """处理ChannelInfo表同步"""
    records = ChannelInfo.objects.filter(sync_flag=sync_flag)
    if records.exists():
        # 待同步记录
        for sync_row in records:
            # 修改同步状态为 - 开始同步
            sync_row.sync_flag = SyncTypes.sync_waiting
            sync_row.save()
            # 生成后台配置表所需字段值
            dbname = sync_row.db_name
            dbname_chn = sync_row.chn_name
            dbname_abb = sync_row.sys_name
            username = sync_row.username
            password = sync_row.password
            dbinst = username
            ip = sync_row.address
            port = sync_row.port
            codepage = sync_row.code_page
            cha_no = sync_row.chn_id
            start_time = sync_row.chn_start_time
            # khd_init = ''
            record_date = datetime.now().strftime('%Y-%m-%d')

            # 拼装并执行DB2 SQL语句
            sql_stmt_chn_del = eval('f' + '"' + get_sql_stmt('CHANNEL_INFO:DELETE') + '"')
            curr.execute(sql_stmt_chn_del)

            sql_stmt_chn_ins = eval('f' + '"' + get_sql_stmt('CHANNEL_INFO:INSERT') + '"')
            curr.execute(sql_stmt_chn_ins)
            # ibm_db.exec_immediate(cur_conn, sql_stmt_chn_ins)

            # 修改状态为已同步
            sync_row.sync_flag = True
            sync_row.save()
