import os
from django.core.wsgi import get_wsgi_application
from datetime import datetime

# 加载django项目环境参数
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "desire.settings")
application = get_wsgi_application()

from datacloud.models import ChannelInfo, ChkInfo, SyncTaskInfo, PushTaskInfo

##########################################
# 生成后台调度配置信息表
##########################################

# 生成渠道信息表
sync_rows = ChannelInfo.objects.filter(sync_flag=False)  # 待同步记录
for sync_row in sync_rows:
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

# 生成条件信息表
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


# 生成任务信息表
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
    # chnnel = sync_row.
##########################################
# 生成后台调度任务表及任务关系依赖
##########################################
