import os
from django.core.wsgi import get_wsgi_application
from datetime import datetime

# 加载django项目环境参数
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "desire.settings")
application = get_wsgi_application()

from datacloud.models import ChannelInfo, ChkInfo, SyncTaskInfo, PushTaskInfo
from datacloud.interface.convert import convert

##########################################
# 生成后台调度配置信息表
##########################################


##########################################
# 生成后台调度任务表及任务关系依赖
##########################################


if __name__ == '__main__':
    channel_info = ChannelInfo.objects.filter(sync_flag=False)
    if channel_info.exists():
        # 待同步记录
        for sync_row in channel_info:
            dbname = sync_row.db_name
            dbname_chn = sync_row.chn_name
            dbname_abb = sync_row.sys_name
            username = sync_row.username
            password = sync_row.password
            dbinst = username
            ip = sync_row.address
            port = sync_row.port
            codepage = sync_row.code_page
            khd_init = ''
            record_date = datetime.now().strftime('%Y-%m-%d')

            # 拼装DB2 SQL语句
            pre_sql1 = f"DELETE FROM TEST.CHANNEL_INFO WHERE DBNAME = '{dbname}'"

            pre_sql2 = f"INSERT INTO TEST.CHANNEL_INFO (DBNAME, DBNAME_CHN, DBNAME_ABB, USERNAME, PASSWORD, " \
                       f"DBINST, IP, PORT, CODEPAGE, KHD_INIT, RECORD_DATE) " \
                       f"VALUES ('{dbname}', '{dbname_chn}', '{dbname_abb}', '{username}', '{password}', '{username}', " \
                       f"'{ip}', '{port}', '{codepage}', '{khd_init}', '{record_date}'); "

            # 调用DB2接口，执行SQL语句
            if convert(pre_sql1, pre_sql2):
                # 修改状态为已同步
                sync_row.sync_flag = True
                sync_row.save()
            else:
                print("convert failed.")

    sync_rows = ChkInfo.objects.filter(sync_flag=False)  # 待同步记录
    for sync_row in sync_rows:
        dbname = sync_row.db_name
        chk_id = sync_row.chk_id
        chk_flag = sync_row.chk_condition
        chk_name = sync_row.chk_name
        date_type = sync_row.date_type
        chk_condition = sync_row.chk_valid_condition
        memo = sync_row.memo
        val_flag = sync_row.val_flag
        record_date = datetime.now().strftime('%Y-%m-%d')

        # 拼装DB2 SQL语句
        pre_sql1 = f"DELETE FROM TEST.CHK_INFO WHERE DBNAME = '{dbname}' AND CHK_ID = {chk_id}"

        pre_sql2 = f"INSERT INTO TEST.CHK_INFO (DBNAME, CHK_ID, CHK_FLAG, CHK_NAME, DATE_TYPE, VAL_FLAG, MEMO, RECORD_DATE) " \
                   f"VALUES ('{dbname}', {chk_id}, '{chk_flag}', '{chk_name}', '{date_type}', " \
                   f"'{val_flag}', '{memo}', '{record_date}'); "

        # 调用DB2接口，执行SQL语句
        if convert(pre_sql1, pre_sql2):
            # 修改状态为已同步
            sync_row.sync_flag = True
            sync_row.save()
        else:
            print("convert failed.")

    sync_rows = SyncTaskInfo.objects.filter(sync_flag=False)  # 待同步记录
    for sync_row in sync_rows:
        dbname = sync_row.db_name
        tabname = sync_row.tab_name
        exp_method = sync_row.exp_method
        zq_info = sync_row.zl_info
        zl_col = sync_row.zl_col
        ftp_file = sync_row.ftp_file
        date_type = sync_row.date_type
        out_path = sync_row.out_path
        outfile_type = sync_row.outfile_type
        load_method = sync_row.load_method
        local_tab_tmp = sync_row.load_tab_tmp
        local_tab_mir = sync_row.load_tab_mir
        month_flag = sync_row.month_flag
        his_flag = sync_row.his_flag
        channel = sync_row.db_name.sys_name
        bak_flag = sync_row.backup_flag
        val_flag = sync_row.val_flag
        record_date = datetime.now().strftime('%Y-%m-%d')

        # 拼装DB2 SQL语句
        pre_sql1 = f"DELETE FROM TEST.TASK_INFO WHERE DBNAME = '{dbname}' AND TABNAME = '{tabname}' "

        pre_sql2 = f"INSERT INTO TEST.TASK_INFO VALUES " \
                   f"('{dbname}', {tabname}, '{exp_method}', '{zq_info}', '{zl_col}', " \
                   f"'{ftp_file}', '{date_type}', '{out_path}', '{outfile_type}', '{load_method}', " \
                   f"'{local_tab_tmp}', '{local_tab_mir}', '{month_flag}', '{his_flag}', " \
                   f"'{channel}', '{bak_flag}', '{val_flag}', 'record_date'); "

        # 调用DB2接口，执行SQL语句
        if convert(pre_sql1, pre_sql2):
            # 修改状态为已同步
            sync_row.sync_flag = True
            sync_row.save()
        else:
            print("convert failed.")

    push_task_info = PushTaskInfo.objects.filter(sync_flag=False)
    if push_task_info.exists():
        # 待同步记录
        # sync_rows = ChannelInfo.objects.filter(sync_flag=False)
        for sync_row in push_task_info:
            tab_name = sync_row.tab_name
            path = sync_row.path
            filetype = sync_row.file_type
            codepage = sync_row.code_page
            separator = sync_row.separator
            delimiter = sync_row.delimiter
            val_flag = sync_row.val_flag
            record_date = record_date = datetime.now().strftime('%Y-%m-%d')

            # 拼装DB2 SQL语句
            pre_sql1 = f"DELETE FROM TEST.PUSH_INFO WHERE TAB_NAME = '{tab_name}' AND CODEPAGE = '{codepage}' AND " \
                       f"SEPARATOR = '{separator}' AND FILETYPE = '{filetype}' AND DELIMITER = '{delimiter}'"

            pre_sql2 = f"INSERT INTO TEST.PUSH_INFO VALUES " \
                       f"('{tab_name}', {path}, '{filetype}', '{codepage}', '{separator}', " \
                       f"'{delimiter}', '{val_flag}', '{record_date}'; "

            # 调用DB2接口，执行SQL语句
            if convert(pre_sql1, pre_sql2):
                # 修改状态为已同步
                sync_row.sync_flag = True
                sync_row.save()
            else:
                print("convert failed.")
