import os
from django.core.wsgi import get_wsgi_application
from datetime import datetime

# 加载django项目环境参数
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "desire.settings")
application = get_wsgi_application()

from datacloud.models import ChannelInfo, ChkInfo, SyncTaskInfo, PushTaskInfo
from datacloud.interface.tools import get_db_conn, get_sql_stmt


if __name__ == "__main__":
    """
    根据前端四张配置表中的未同步记录：Sync_Flag值为False
    关联更新后端ETL表中的记录
    更新方法：根据主键先删除再插入
    """

    # 取数据库游标
    curr = get_db_conn('ETL-Database')

    ##########################################
    # 生成渠道信息配置表：
    # 根据ChannelInfo表中未同步的记录
    # 对ETL DB中配置表的对应记录进行新增或更新
    ##########################################

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
            cha_no = sync_row.chn_id
            start_time = sync_row.chn_start_time
            # khd_init = ''
            record_date = datetime.now().strftime('%Y-%m-%d')

            # 拼装并执行DB2 SQL语句
            sql_stmt_chn_del = eval('f' + '"' + get_sql_stmt('CHANNEL_INFO:DELETE') + '"')
            curr.execute(sql_stmt_chn_del)
            # ibm_db.exec_immediate(cur_conn, sql_stmt_chn_del)

            sql_stmt_chn_ins = eval('f' + '"' + get_sql_stmt('CHANNEL_INFO:INSERT') + '"')
            curr.execute(sql_stmt_chn_ins)
            # ibm_db.exec_immediate(cur_conn, sql_stmt_chn_ins)

            # 修改状态为已同步
            sync_row.sync_flag = True
            sync_row.save()

    ##########################################
    # 生成检测条件信息配置表：
    # 根据ChkInfo表中未同步的记录
    # 对ETL DB中配置表的对应记录进行新增或更新
    ##########################################

    sync_rows = ChkInfo.objects.filter(sync_flag=False)  # 待同步记录
    for sync_row in sync_rows:
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
        sql_stmt_chk_del = eval('f' + '"' + get_sql_stmt('CHK_INFO:DELETE') + '"')
        curr.execute(sql_stmt_chk_del)
        # ibm_db.exec_immediate(cur_conn, sql_stmt_chk_del)
        sql_stmt_chk_ins = eval('f' + '"' + get_sql_stmt('CHK_INFO:INSERT') + '"')
        curr.execute(sql_stmt_chk_ins)
        # ibm_db.exec_immediate(cur_conn, sql_stmt_chk_ins)

        # 修改状态为已同步
        sync_row.sync_flag = True
        sync_row.save()

    ##########################################
    # 生成数据同步加载任务配置表：
    # 根据SyncTaskInfo表中未同步的记录
    # 对ETL DB中配置表的对应记录进行新增或更新
    ##########################################

    sync_rows = SyncTaskInfo.objects.filter(sync_flag=False)  # 待同步记录
    for sync_row in sync_rows:
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
        local_tab_tmp = '' if sync_row.load_tab_tmp is None else sync_row.load_tab_tmp
        local_tab_mir = '' if sync_row.local_tab_mir is None else sync_row.local_tab_mir
        month_flag = int(sync_row.month_flag)
        his_flag = int(sync_row.his_flag)
        his_cyc = '' if sync_row.his_frequency is None else sync_row.his_frequency
        bak_flag = int(sync_row.backup_flag)
        val_flag = int(sync_row.val_flag)
        record_date = datetime.now().strftime('%Y-%m-%d')

        # 拼装并执行DB2 SQL语句
        sql_stmt_sync_del = eval('f' + '"' + get_sql_stmt('TASK_INFO:DELETE') + '"')
        curr.execute(sql_stmt_sync_del)
        # ibm_db.exec_immediate(cur_conn, sql_stmt_sync_del)
        sql_stmt_sync_ins = eval('f' + '"' + get_sql_stmt('TASK_INFO:INSERT') + '"')
        curr.execute(sql_stmt_sync_ins)
        # ibm_db.exec_immediate(cur_conn, sql_stmt_sync_ins)

        # 修改状态为已同步
        sync_row.sync_flag = True
        sync_row.save()

    ##########################################
    # 生成数据推送任务配置表：
    # 根据PushTaskInfo表中未同步的记录
    # 对ETL DB中配置表的对应记录进行新增或更新
    ##########################################

    push_task_info = PushTaskInfo.objects.filter(sync_flag=False)
    if push_task_info.exists():
        # 待同步记录
        for sync_row in push_task_info:
            tab_name = sync_row.push_tab_name
            path = sync_row.path
            filetype = sync_row.file_type
            codepage = sync_row.code_page
            separator = '' if sync_row.separator is None else sync_row.separator
            delimiter = '' if sync_row.delimiter is None else sync_row.delimiter
            val_flag = int(sync_row.val_flag)
            record_date = datetime.now().strftime('%Y-%m-%d')

            # 拼装并执行DB2 SQL语句
            sql_stmt_push_del = eval('f' + '"' + get_sql_stmt('PUSH_INFO:DELETE') + '"')
            curr.execute(sql_stmt_push_del)
            # ibm_db.exec_immediate(cur_conn, sql_stmt_push_del)
            sql_stmt_push_ins = eval('f' + '"' + get_sql_stmt('PUSH_INFO:INSERT') + '"')
            curr.execute(sql_stmt_push_ins)
            # ibm_db.exec_immediate(cur_conn, sql_stmt_push_ins)

            # 修改状态为已同步
            sync_row.sync_flag = True
            sync_row.save()
