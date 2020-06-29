import os
from django.core.wsgi import get_wsgi_application
from datetime import datetime
import ibm_db
from desire.settings import INTERFACE_DIR
from datacloud.interface.tools import get_db_conn, get_sql_stmt

# 加载django项目环境参数
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "desire.settings")
application = get_wsgi_application()

from datacloud.models import ChannelInfo, ChkInfo, SyncTaskInfo, PushTaskInfo, ScriptConfig

##########################################
# 生成后台调度配置信息表
##########################################

if __name__ == '__main__':

    # db_conn = get_db_conn('ETL-Database')
    # cur_conn = ibm_db.connect(db_conn, "", "")

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
            chn_sql1 = eval('f' + '"' + get_sql_stmt('SCTCHA') + '"')
            chn_sql2 = eval('f' + '"' + get_sql_stmt('SCTMSG_JOB_REL') + '"')

            # 执行DB2 SQL语句
            # ibm_db.exec_immediate(cur_conn, chn_sql1)
            # ibm_db.exec_immediate(cur_conn, chn_sql2)

            # 执行完成后，将该条记录的新增记录标识为否
            # chn.new_record_flag = False
            # chn.save()

    chk_info = ChkInfo.objects.filter(new_record_flag=True)
    if chk_info:
        # 插入 InitJob
        for chk in chk_info:
            ID = chk.chk_id
            JOBTYPE = 1
            JOBCNM = chk.chk_name
            JOBID = chk.chk_id
            JOBPRI = 1
            STGID = 10000
            CHAID = chk.db_name.chn_id
            JOBCYC = 'D'
            APPURL = ScriptConfig.objects.get(type=10000).script
            PARAM = ''
            JOBVAL = 1
            JOBIGN = 0

            # 拼接DB2 SQL语句
            chk_sql1 = eval('f' + '"' + get_sql_stmt('INIT_JOB') + '"')


##########################################
# 生成后台调度任务表及任务关系依赖
##########################################
