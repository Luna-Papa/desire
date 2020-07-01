import os
from django.core.wsgi import get_wsgi_application
from datetime import datetime
import ibm_db
from datacloud.interface.tools import get_db_conn, get_sql_stmt

# 加载django项目环境参数
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "desire.settings")
application = get_wsgi_application()

from datacloud.models import ChannelInfo, ChkInfo, SyncTaskInfo, PushTaskInfo, ScriptConfig

if __name__ == '__main__':

    db_conn = get_db_conn('ETL-Database')
    # cur_conn = ibm_db.connect(db_conn, "", "")

    ##########################################
    # 处理渠道配置表
    ##########################################

    channel_info = ChannelInfo.objects.filter(new_record_flag=True)
    if channel_info:
        """
        渠道配置需要写入调度表 <SCTCHA> 和 <SCTMSG_JOB_REL>
        """
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
            chn_sql_cha = eval('f' + '"' + get_sql_stmt('SCTCHA') + '"')
            chn_sql_rel = eval('f' + '"' + get_sql_stmt('SCTMSG_JOB_REL') + '"')

            # 执行DB2 SQL语句
            # ibm_db.exec_immediate(cur_conn, chn_sql_cha)
            # ibm_db.exec_immediate(cur_conn, chn_sql_rel)

            # 生成渠道首作业信息
            ID = chn.chn_id + 1
            JOBTYPE = 1
            JOBCNM = f'渠道收作业-{chn.chn_name}'
            JOBID = chn.chn_id + 1
            JOBPRI = 1
            STGID = 1
            CHAID = chn.chn_id + 1
            JOBCYC = 'D'
            APPURL = ScriptConfig.objects.get(type=1).script
            PARAM = ''
            JOBVAL = 1
            JOBIGN = 0

            chn_sql_init_begin = eval('f' + '"' + get_sql_stmt('INIT_JOB') + '"')
            # ibm_db.exec_immediate(cur_conn, chn_sql_init_begin)

            """
            一个渠道对应一个备份作业，此处需要将备份作业的相关信息生成到InitJob，
            但此时不能插入作业依赖关系： 渠道完成 -> 备份，
            一个渠道可能有多个完成作业，因此渠道完成到备份是多对一。
            """
            ID = chn.chn_backup_id
            JOBTYPE = 1
            JOBCNM = f'数据备份-{chn.chn_name}'
            JOBID = chn.chn_backup_id
            JOBPRI = 1
            STGID = 50000
            CHAID = chn.chn_id
            JOBCYC = 'D'
            APPURL = ScriptConfig.objects.get(type=50000).script
            PARAM = ''
            JOBVAL = 1
            JOBIGN = 0

            chn_sql_init_back = eval('f' + '"' + get_sql_stmt('INIT_JOB') + '"')
            # ibm_db.exec_immediate(cur_conn, chn_sql_init_back)

            # 执行完成后，将该条记录的新增记录标识为否
            # chn.new_record_flag = False
            # chn.save()

    ##########################################
    # 处理渠道检测配置表
    ##########################################

    chk_info = ChkInfo.objects.filter(new_record_flag=True)
    if chk_info:
        for chk in chk_info:
            # InitJob所需字段
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

            # SCTFLW所需字段
            FLWJOB = chk.chk_id
            FLWPRO = chk.db_name.chn_id + 1

            # 拼接DB2 SQL语句
            chk_sql1 = eval('f' + '"' + get_sql_stmt('INIT_JOB') + '"')
            chk_sql2 = eval('f' + '"' + get_sql_stmt('SCTFLW') + '"')  # 依赖关系：渠道首作业 -> 检测

            # 执行DB2 SQL语句
            # ibm_db.exec_immediate(cur_conn, chk_sql1)
            # ibm_db.exec_immediate(cur_conn, chk_sql2)

            # 生成渠道完成作业信息
            ID = chk.chk_done_id
            JOBTYPE = 1
            JOBCNM = f'数据检测-{chk.chk_name}-完成'
            JOBID = chk.chk_done_id
            JOBPRI = 1
            STGID = 40000
            CHAID = chk.db_name.chn_id
            JOBCYC = 'D'
            APPURL = ScriptConfig.objects.get(type=40000).script
            PARAM = ''
            JOBVAL = 1
            JOBIGN = 0

            chk_sql3 = eval('f' + '"' + get_sql_stmt('INIT_JOB') + '"')
            # ibm_db.exec_immediate(cur_conn, chk_sql3)

            # 生成渠道完成作业与备份作业的依赖关系
            FLWJOB = chk.db_name.chn_backup_id
            FLWPRO = chk.chk_done_id
            chk_sql4 = eval('f' + '"' + get_sql_stmt('SCTFLW') + '"')  # 依赖关系：渠道完成作业 -> 备份
            # ibm_db.exec_immediate(cur_conn, chk_sql4)

            # 执行完成后，将该条记录的新增记录标识为否
            # chk.new_record_flag = False
            # chk.save()

    ##########################################
    # 处理数据同步卸载任务表
    ##########################################

    sync_task_info = SyncTaskInfo.objects.filter(new_record_flag=True)
    if sync_task_info:
        for sync_task in sync_task_info:
            # 1、先处理数据同步任务

            # InitJob所需字段
            ID = sync_task.sync_id
            JOBTYPE = 1
            JOBCNM = f'数据卸载-{sync_task.db_name.chn_name}-{sync_task.tab_name}'
            JOBID = sync_task.sync_id
            JOBPRI = 1
            STGID = 20000
            CHAID = sync_task.db_name.chn_id
            JOBCYC = 'D'
            APPURL = ScriptConfig.objects.get(type=20000).script
            PARAM = ''
            JOBVAL = 1
            JOBIGN = 0

            # SCTFLW所需字段
            FLWJOB = sync_task.sync_id
            FLWPRO = sync_task.chk_name.chk_id

            # 拼接DB2 SQL语句
            sync_task_sql1 = eval('f' + '"' + get_sql_stmt('INIT_JOB') + '"')
            sync_task_sql2 = eval('f' + '"' + get_sql_stmt('SCTFLW') + '"')  # 依赖关系：检测 -> 卸载

            # 执行DB2 SQL语句
            # ibm_db.exec_immediate(cur_conn, sync_task_sql1)
            # ibm_db.exec_immediate(cur_conn, sync_task_sql2)

            # 2、 再处理数据装载任务

            # InitJob所需字段
            ID = sync_task.load_id
            JOBTYPE = 1
            JOBCNM = f'数据装载-{sync_task.db_name.chn_name}-{sync_task.tab_name}'
            JOBID = sync_task.load_id
            JOBPRI = 1
            STGID = 30000
            CHAID = sync_task.db_name.chn_id
            JOBCYC = 'D'
            APPURL = ScriptConfig.objects.get(type=30000).script
            PARAM = ''
            JOBVAL = 1
            JOBIGN = 0

            # SCTFLW所需字段
            FLWJOB = sync_task.load_id
            FLWPRO = sync_task.sync_id

            # 拼接DB2 SQL语句
            load_task_sql1 = eval('f' + '"' + get_sql_stmt('INIT_JOB') + '"')
            load_task_sql2 = eval('f' + '"' + get_sql_stmt('SCTFLW') + '"')  # 依赖关系：卸载 -> 装载

            # 执行DB2 SQL语句
            # ibm_db.exec_immediate(cur_conn, load_task_sql1)
            # ibm_db.exec_immediate(cur_conn, load_task_sql2)

            # 生成装载任务与渠道完成任务依赖关系

            # SCTFLW所需字段
            FLWJOB = sync_task.chk_name.chk_done_id
            FLWPRO = sync_task.load_id

            load_task_sql3 = eval('f' + '"' + get_sql_stmt('SCTFLW') + '"')  # 依赖关系：装载 -> 渠道完成
            # ibm_db.exec_immediate(cur_conn, load_task_sql3)

            # 执行完成后，将该条记录的新增记录标识为否
            # sync_task.new_record_flag = False
            # sync_task.save()

    ##########################################
    # 处理数据推送任务表
    ##########################################

    push_task_info = PushTaskInfo.objects.filter(new_record_flag=True)
    if push_task_info:
        for push_task in push_task_info:
            # InitJob所需字段
            ID = push_task.push_id
            JOBTYPE = 1
            JOBCNM = f'数据推送-{push_task.db_name.chn_name}-{push_task.push_tab_name}'
            JOBID = push_task.push_id
            JOBPRI = 1
            STGID = 60000
            CHAID = push_task.db_name.chn_id
            JOBCYC = 'D'
            APPURL = ScriptConfig.objects.get(type=60000).script
            PARAM = ''
            JOBVAL = 1
            JOBIGN = 0

            # SCTFLW所需字段
            FLWJOB = push_task.push_id
            FLWPRO = push_task.source_tab_name.chk_name.chk_done_id

            # 拼接DB2 SQL语句
            push_task_sql1 = eval('f' + '"' + get_sql_stmt('INIT_JOB') + '"')
            push_task_sql2 = eval('f' + '"' + get_sql_stmt('SCTFLW') + '"')  # 依赖关系：渠道检测完成 -> 推送

            # 执行DB2 SQL语句
            # ibm_db.exec_immediate(cur_conn, push_task_sql1)
            # ibm_db.exec_immediate(cur_conn, push_task_sql2)

            # 执行完成后，将该条记录的新增记录标识为否
            # push_task.new_record_flag = False
            # push_task.save()
