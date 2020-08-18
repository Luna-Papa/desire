import os
import pathlib
from django.core.wsgi import get_wsgi_application
from datetime import datetime

# 加载django项目环境参数
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "desire.settings")
application = get_wsgi_application()
# 导入相关模型
from datacloud.models import ChannelInfo, ChkInfo, SyncTaskInfo, PushTaskInfo, \
    PushSysInfo, PushSysTabInfo, SyncTypes
from datacloud.interface.tools import get_db_conn, get_sql_stmt


#########################################################
# 根据前台配置表中的未同步记录：Sync_Flag值为False
# 关联更新后台配置表中的记录
# 更新方法：根据主键先删除再插入
#########################################################


def channel_info(sync_flag=SyncTypes.sync_waiting, curr=get_db_conn('ETL-Database')):
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
            record_date = datetime.now().strftime('%Y-%m-%d')

            # 拼装并执行DB2 SQL语句
            del_sql_stmt = eval('f' + '"' + get_sql_stmt('ChannelInfo:DELETE') + '"')
            ins_sql_stmt = eval('f' + '"' + get_sql_stmt('ChannelInfo:INSERT') + '"')
            try:
                curr.execute(del_sql_stmt)
                curr.execute(ins_sql_stmt)
                # 同步完成后，修改前台表同步状态为 - 同步完成
                sync_row.sync_flag = SyncTypes.sync_complete
                sync_row.save()
            except Exception as e:
                sync_row.sync_flag = SyncTypes.sync_failed
                sync_row.save()


def chk_info(sync_flag=SyncTypes.sync_waiting, curr=get_db_conn('ETL-Database')):
    """处理ChkInfo表同步"""
    records = ChkInfo.objects.filter(sync_flag=sync_flag)
    if records.exists():
        # 待同步记录
        for sync_row in records:
            # 修改同步状态为 - 开始同步
            sync_row.sync_flag = SyncTypes.sync_waiting
            sync_row.save()

            # 生成后台配置表所需字段值
            dbname = sync_row.chn_name.db_name
            chk_id = sync_row.chk_id
            chk_flag = sync_row.chk_condition.replace('\'', '\'\'')
            chk_name = sync_row.chk_name
            date_type = sync_row.date_type
            chk_condition = sync_row.chk_valid_condition
            memo = '' if sync_row.memo is None else sync_row.memo
            val_flag = int(sync_row.val_flag)
            record_date = datetime.now().strftime('%Y-%m-%d')

            # 拼装并执行DB2 SQL语句
            del_sql_stmt = eval('f' + '"' + get_sql_stmt('ChkInfo:DELETE') + '"')
            ins_sql_stmt = eval('f' + '"' + get_sql_stmt('ChkInfo:INSERT') + '"')
            try:
                curr.execute(del_sql_stmt)
                curr.execute(ins_sql_stmt)
                # 同步完成后，修改前台表同步状态为 - 同步完成
                sync_row.sync_flag = SyncTypes.sync_complete
                sync_row.save()
            except Exception as e:
                sync_row.sync_flag = SyncTypes.sync_failed
                sync_row.save()


def sync_task_info(sync_flag=SyncTypes.sync_waiting, curr=get_db_conn('ETL-Database')):
    """处理SyncTaskInfo表同步"""
    records = SyncTaskInfo.objects.filter(sync_flag=sync_flag)
    if records.exists():
        # 待同步记录
        for sync_row in records:
            # 修改同步状态为 - 开始同步
            sync_row.sync_flag = SyncTypes.sync_waiting
            sync_row.save()

            # 生成后台配置表所需字段值
            dbname = sync_row.chn_name.db_name
            tabname = sync_row.tab_name
            exp_method = sync_row.exp_method
            zq_info = sync_row.zl_info
            zl_col = sync_row.zl_col
            ftp_file = '' if sync_row.ftp_file is None else sync_row.ftp_file
            date_type = sync_row.date_type
            out_path = sync_row.out_path
            outfile_type = sync_row.outfile_type
            load_method = sync_row.load_method
            local_tab_tmp = sync_row.load_tab_tmp if sync_row.load_tab_tmp else ''
            local_tab_mir = sync_row.load_tab_mir if sync_row.load_tab_mir else ''
            month_flag = int(sync_row.month_flag)
            his_flag = int(sync_row.his_flag)
            his_cyc = sync_row.his_frequency if sync_row.his_frequency else ''
            his_tab = sync_row.his_tab if sync_row.his_tab else ''
            bak_flag = int(sync_row.backup_flag)
            channel = sync_row.chn_name.sys_name if sync_row.backup_flag else ''
            val_flag = int(sync_row.val_flag)
            record_date = datetime.now().strftime('%Y-%m-%d')

            # 拼装并执行DB2 SQL语句
            del_sql_stmt = eval('f' + '"' + get_sql_stmt('SyncTaskInfo:DELETE') + '"')
            ins_sql_stmt = eval('f' + '"' + get_sql_stmt('SyncTaskInfo:INSERT') + '"')
            try:
                curr.execute(del_sql_stmt)
                curr.execute(ins_sql_stmt)
                # 同步完成后，修改前台表同步状态为 - 同步完成
                sync_row.sync_flag = SyncTypes.sync_complete
                sync_row.save()
            except Exception as e:
                sync_row.sync_flag = SyncTypes.sync_failed
                sync_row.save()


def push_task_info(sync_flag=SyncTypes.sync_waiting, curr=get_db_conn('ETL-Database')):
    """处理PushTaskInfo表同步"""
    records = PushTaskInfo.objects.filter(sync_flag=sync_flag)
    if records.exists():
        # 待同步记录
        for sync_row in records:
            # 修改同步状态为 - 开始同步
            sync_row.sync_flag = SyncTypes.sync_waiting
            sync_row.save()

            # 生成后台配置表所需字段值
            tab_name = sync_row.push_tab_name
            path = sync_row.path
            filetype = sync_row.file_type
            codepage = sync_row.code_page
            separator = '' if sync_row.separator is None else sync_row.separator
            delimiter = '' if sync_row.delimiter is None else sync_row.delimiter
            val_flag = int(sync_row.val_flag)
            record_date = datetime.now().strftime('%Y-%m-%d')

            # 拼装并执行DB2 SQL语句
            del_sql_stmt = eval('f' + '"' + get_sql_stmt('PushTaskInfo:DELETE') + '"')
            ins_sql_stmt = eval('f' + '"' + get_sql_stmt('PushTaskInfo:INSERT') + '"')
            try:
                curr.execute(del_sql_stmt)
                curr.execute(ins_sql_stmt)
                # 同步完成后，修改前台表同步状态为 - 同步完成
                sync_row.sync_flag = SyncTypes.sync_complete
                sync_row.save()
            except Exception as e:
                sync_row.sync_flag = SyncTypes.sync_failed
                sync_row.save()


def push_sys_info(sync_flag=SyncTypes.sync_waiting, curr=get_db_conn('ETL-Database')):
    """处理PushSysInfo表同步"""
    records = PushSysInfo.objects.filter(sync_flag=sync_flag)
    if records.exists():
        # 待同步记录
        for sync_row in records:
            # 修改同步状态为 - 开始同步
            sync_row.sync_flag = SyncTypes.sync_waiting
            sync_row.save()

            # 生成后台配置表所需字段值
            system_abbr = sync_row.system_abbr
            pushpath = sync_row.push_path

            # 拼装并执行DB2 SQL语句
            del_sql_stmt = eval('f' + '"' + get_sql_stmt('PushSysInfo:DELETE') + '"')
            ins_sql_stmt = eval('f' + '"' + get_sql_stmt('PushSysInfo:INSERT') + '"')
            try:
                curr.execute(del_sql_stmt)
                curr.execute(ins_sql_stmt)
                # 同步完成后，修改前台表同步状态为 - 同步完成
                sync_row.sync_flag = SyncTypes.sync_complete
                sync_row.save()
            except Exception as e:
                sync_row.sync_flag = SyncTypes.sync_failed
                sync_row.save()


def push_sys_tab_info(sync_flag=SyncTypes.sync_waiting, curr=get_db_conn('ETL-Database')):
    """处理PushSysTabInfo表同步"""
    records = PushSysTabInfo.objects.filter(sync_flag=sync_flag)
    if records.exists():
        # 待同步记录
        for sync_row in records:
            # 修改同步状态为 - 开始同步
            sync_row.sync_flag = SyncTypes.sync_waiting
            sync_row.save()

            # 生成后台配置表所需字段值
            system_name = sync_row.system_name.system_name
            system_abbr = sync_row.system_name.system_abbr
            tab_id = sync_row.tab_id.push_tab_id
            channel = sync_row.tab_id.chn_name.sys_name
            val_flag = int(sync_row.val_flag)

            # 拼装并执行DB2 SQL语句
            del_sql_stmt = eval('f' + '"' + get_sql_stmt('PushSysTabInfo:DELETE') + '"')
            ins_sql_stmt = eval('f' + '"' + get_sql_stmt('PushSysTabInfo:INSERT') + '"')
            try:
                curr.execute(del_sql_stmt)
                curr.execute(ins_sql_stmt)
                # 同步完成后，修改前台表同步状态为 - 同步完成
                sync_row.sync_flag = SyncTypes.sync_complete
                sync_row.save()
            except Exception as e:
                sync_row.sync_flag = SyncTypes.sync_failed
                sync_row.save()
