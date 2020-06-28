import os
from django.core.wsgi import get_wsgi_application
from datetime import datetime

# 加载django项目环境参数
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "desire.settings")
application = get_wsgi_application()

from datacloud.models import ChannelInfo, ChkInfo, SyncTaskInfo, PushTaskInfo, ScriptConfig
from datacloud.interface.convert import convert

##########################################
# 生成后台调度配置信息表
##########################################
channel_info = ChannelInfo.objects.filter(new_record_flag=True)
if channel_info:
    # 插入调度表 <SCTCHA> 和 <SCTMSG_JOB_REL>
    for chn in channel_info:

        # STCHA所需字段
        CHAID = chn.chn_id
        CHANAME = chn.chn_name
        CHADATE = datetime.now().strftime('%Y-%m-%d')
        CHASTU = 2
        CHADES = chn.sys_name
        ETLSTU = 1

        # SCTMSG_JOB_REL所需字段
        MSGCODE = str(chn.chn_id + 1)
        JOBID = chn.chn_id + 1
        MSGVAL = 1

        # 拼接DB2 SQL语句
        pre_sql_01 = f"INSERT INTO ODSUSER.SCTCHA VALUES " \
                  f"({CHAID}, '{CHANAME}', '{CHADATE}', {CHASTU}, '{CHADES}', {ETLSTU})"

        pre_sql_02 = f"INSERT INTO ODSUSER.SCTMSG_JOB_REL VALUES " \
                     f"('{MSGCODE}', {JOBID}, {MSGVAL})"

        # 执行DB2 SQL语句

        # 执行完成后，将该条记录的新增记录标识为否
        # chn.new_record_flag = False
        # chn.save()

chk_info = ChkInfo.objects.filter(new_record_flag=True)
if chk_info:
    # 插入 InitJob
    for chk in chk_info:
        chk.chk_id
##########################################
# 生成后台调度任务表及任务关系依赖
##########################################
