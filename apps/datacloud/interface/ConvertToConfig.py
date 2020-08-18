import os
from django.core.wsgi import get_wsgi_application
from datetime import datetime

# 加载django项目环境参数
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "desire.settings")
application = get_wsgi_application()

from datacloud.models import ChannelInfo, ChkInfo, SyncTaskInfo, PushTaskInfo, \
    SmsSenderInfo, PushSysInfo, PushSysTabInfo, SyncTypes
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

    channel_info = ChannelInfo.objects.filter(sync_flag=SyncTypes.sync_waiting)
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

    ##########################################
    # 生成检测条件信息配置表：
    # 根据ChkInfo表中未同步的记录
    # 对ETL DB中配置表的对应记录进行新增或更新
    ##########################################

    sync_rows = ChkInfo.objects.filter(sync_flag=SyncTypes.sync_waiting)  # 待同步记录
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
        del_sql_stmt = eval('f' + '"' + get_sql_stmt('ChkInfo:DELETE') + '"')
        # curr.execute(sql_stmt_chk_del)
        # ibm_db.exec_immediate(cur_conn, sql_stmt_chk_del)
        ins_sql_stmt = eval('f' + '"' + get_sql_stmt('ChkInfo:INSERT') + '"')
        # curr.execute(sql_stmt_chk_ins)
        # ibm_db.exec_immediate(cur_conn, sql_stmt_chk_ins)

        try:
            curr.execute(del_sql_stmt)
            curr.execute(ins_sql_stmt)
            # 同步完成后，修改前台表同步状态为 - 同步完成
            sync_row.sync_flag = SyncTypes.sync_complete
            sync_row.save()
        except Exception as e:
            sync_row.sync_flag = SyncTypes.sync_failed
            sync_row.save()

    ##########################################
    # 生成数据同步加载任务配置表：
    # 根据SyncTaskInfo表中未同步的记录
    # 对ETL DB中配置表的对应记录进行新增或更新
    ##########################################

    sync_rows = SyncTaskInfo.objects.filter(sync_flag=SyncTypes.sync_waiting)  # 待同步记录
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
        # curr.execute(sql_stmt_sync_del)
        # ibm_db.exec_immediate(cur_conn, sql_stmt_sync_del)
        ins_sql_stmt = eval('f' + '"' + get_sql_stmt('SyncTaskInfo:INSERT') + '"')
        # curr.execute(sql_stmt_sync_ins)
        # ibm_db.exec_immediate(cur_conn, sql_stmt_sync_ins)

        try:
            curr.execute(del_sql_stmt)
            curr.execute(ins_sql_stmt)
            # 同步完成后，修改前台表同步状态为 - 同步完成
            sync_row.sync_flag = SyncTypes.sync_complete
            sync_row.save()
        except Exception as e:
            sync_row.sync_flag = SyncTypes.sync_failed
            sync_row.save()

    ##########################################
    # 生成数据推送任务配置表：
    # 根据PushTaskInfo表中未同步的记录
    # 对ETL DB中配置表的对应记录进行新增或更新
    ##########################################

    push_task_info = PushTaskInfo.objects.filter(sync_flag=SyncTypes.sync_waiting)
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
            del_sql_stmt = eval('f' + '"' + get_sql_stmt('PushTaskInfo:DELETE') + '"')
            # curr.execute(sql_stmt_push_del)
            # ibm_db.exec_immediate(cur_conn, sql_stmt_push_del)
            ins_sql_stmt = eval('f' + '"' + get_sql_stmt('PushTaskInfo:INSERT') + '"')
            # curr.execute(sql_stmt_push_ins)
            # ibm_db.exec_immediate(cur_conn, sql_stmt_push_ins)

            try:
                curr.execute(del_sql_stmt)
                curr.execute(ins_sql_stmt)
                # 同步完成后，修改前台表同步状态为 - 同步完成
                sync_row.sync_flag = SyncTypes.sync_complete
                sync_row.save()
            except Exception as e:
                sync_row.sync_flag = SyncTypes.sync_failed
                sync_row.save()

    ##########################################
    # 生成短信配置表：
    # 根据SmsSenderInfo表中未同步的记录
    # 对ETL DB中配置表的对应记录进行新增或更新
    ##########################################
    sms_sender_info = SmsSenderInfo.objects.filter(sync_flag=SyncTypes.sync_waiting)
    if sms_sender_info.exists():
        # 待同步记录
        for sync_row in sms_sender_info:
            name = sync_row.name
            phone = sync_row.phone
            val_flag = int(sync_row.val_flag)
            record_date = datetime.now().strftime('%Y-%m-%d')

            # 拼装并执行DB2 SQL语句
            del_sql_stmt = eval('f' + '"' + get_sql_stmt('SMS_SENDER:DELETE') + '"')
            # curr.execute(sql_stmt_sms_del)
            # ibm_db.exec_immediate(cur_conn, sql_stmt_push_del)
            ins_sql_stmt = eval('f' + '"' + get_sql_stmt('SMS_SENDER:INSERT') + '"')
            # curr.execute(sql_stmt_sms_ins)
            # ibm_db.exec_immediate(cur_conn, sql_stmt_push_ins)

            try:
                curr.execute(del_sql_stmt)
                curr.execute(ins_sql_stmt)
                # 同步完成后，修改前台表同步状态为 - 同步完成
                sync_row.sync_flag = SyncTypes.sync_complete
                sync_row.save()
            except Exception as e:
                sync_row.sync_flag = SyncTypes.sync_failed
                sync_row.save()

    ##########################################
    # 生成推送系统定义表：
    # 根据PushSysInfo表中未同步的记录
    # 对ETL DB中配置表的对应记录进行新增或更新
    ##########################################
    push_sys_info = PushSysInfo.objects.filter(sync_flag=SyncTypes.sync_waiting)
    if push_sys_info.exists():
        # 待同步记录
        for sync_row in push_sys_info:
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

    ##########################################
    # 生成推送系统定义表：
    # 根据PushSysTabInfo表中未同步的记录
    # 对ETL DB中配置表的对应记录进行新增或更新
    ##########################################

    """处理PushSysTabInfo表同步"""
    push_sys_tab_info = PushSysTabInfo.objects.filter(sync_flag=SyncTypes.sync_waiting)
    if push_sys_tab_info.exists():
        # 待同步记录
        for sync_row in push_sys_tab_info:
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
                print(e)
                sync_row.sync_flag = SyncTypes.sync_failed
                sync_row.save()
