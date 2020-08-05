import os
from django.core.wsgi import get_wsgi_application
from datetime import datetime
from datacloud.interface.tools import get_db_conn, get_sql_stmt

# 加载django项目环境参数
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "desire.settings")
application = get_wsgi_application()

from datacloud.models import ChannelInfo, ChkInfo, SyncTaskInfo, PushTaskInfo, ScriptConfig

SHELL_HOME = '${user.home}/eDataMover/script/'

if __name__ == '__main__':
    """
    前端配置表新增记录时，在后端ETL调度表生成相关记录的处理过程。
    """

    # 取数据库游标
    curr = get_db_conn('ETL-Database')

    ##########################################
    # 处理渠道配置表
    ##########################################

    channel_info = ChannelInfo.objects.filter(new_record_flag=True)
    if channel_info.exists():
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
            curr.execute(chn_sql_cha)
            curr.execute(chn_sql_rel)

            # 生成渠道首作业信息
            ID = chn.chn_id + 1
            JOBTYPE = 1
            JOBCNM = f'渠道首作业-{chn.chn_name}'
            JOBID = chn.chn_id + 1
            JOBPRI = 1
            STGID = 1
            CHAID = chn.chn_id
            JOBCYC = 'D'
            APPURL = SHELL_HOME + ScriptConfig.objects.get(type='1').script
            PARAM = ''
            JOBVAL = 1
            JOBIGN = 0

            chn_sql_init_begin = eval('f' + '"' + get_sql_stmt('INIT_JOB') + '"')
            # ibm_db.exec_immediate(cur_conn, chn_sql_init_begin)
            curr.execute(chn_sql_init_begin)

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
            APPURL = SHELL_HOME + ScriptConfig.objects.get(type='50000').script
            # 备份作业参数为渠道名称
            PARAM = chn.sys_name
            JOBVAL = 1
            JOBIGN = 0

            chn_sql_init_back = eval('f' + '"' + get_sql_stmt('INIT_JOB') + '"')
            # ibm_db.exec_immediate(cur_conn, chn_sql_init_back)
            curr.execute(chn_sql_init_back)

            # 执行完成后，将该条记录的新增记录标识为否
            chn.new_record_flag = False
            chn.save()

    ##########################################
    # 处理渠道检测配置表
    ##########################################

    chk_info = ChkInfo.objects.filter(new_record_flag=True)
    if chk_info.exists():
        for chk in chk_info:
            # InitJob所需字段
            ID = chk.chk_id
            JOBTYPE = 1
            JOBCNM = f'渠道检测-{chk.chk_name}'
            JOBID = chk.chk_id
            JOBPRI = 1
            STGID = 10000
            CHAID = chk.chn_name.chn_id
            JOBCYC = 'D'
            APPURL = SHELL_HOME + ScriptConfig.objects.get(type='10000').script
            # 数据检测类任务参数为db_name
            PARAM = chk.chn_name.db_name
            JOBVAL = 1
            JOBIGN = 0

            # SCTFLW所需字段
            FLWJOB = chk.chk_id
            FLWPRO = chk.chn_name.chn_id + 1

            # 拼接DB2 SQL语句
            chk_sql1 = eval('f' + '"' + get_sql_stmt('INIT_JOB') + '"')
            chk_sql2 = eval('f' + '"' + get_sql_stmt('SCTFLW') + '"')  # 依赖关系：渠道首作业 -> 检测

            # 执行DB2 SQL语句
            curr.execute(chk_sql1)
            curr.execute(chk_sql2)
            # ibm_db.exec_immediate(cur_conn, chk_sql1)
            # ibm_db.exec_immediate(cur_conn, chk_sql2)

            # 生成渠道完成作业信息
            ID = chk.chk_done_id
            JOBTYPE = 1
            JOBCNM = f'渠道-{chk.chk_name}-完成'
            JOBID = chk.chk_done_id
            JOBPRI = 1
            STGID = 40000
            CHAID = chk.chn_name.chn_id
            JOBCYC = 'D'
            APPURL = SHELL_HOME + ScriptConfig.objects.get(type='40000').script
            # 渠道完成作业参数为空
            PARAM = ''
            JOBVAL = 1
            JOBIGN = 0

            chk_sql3 = eval('f' + '"' + get_sql_stmt('INIT_JOB') + '"')
            curr.execute(chk_sql3)
            # ibm_db.exec_immediate(cur_conn, chk_sql3)

            # 生成渠道完成作业与备份作业的依赖关系
            FLWJOB = chk.chn_name.chn_backup_id
            FLWPRO = chk.chk_done_id

            chk_sql4 = eval('f' + '"' + get_sql_stmt('SCTFLW') + '"')  # 依赖关系：渠道完成作业 -> 备份
            curr.execute(chk_sql4)
            # ibm_db.exec_immediate(cur_conn, chk_sql4)

            # 生成渠道完成通知短信作业信息
            ID = chk.chk_done_id + 50000  # 短信作业号是90000开头
            JOBTYPE = 1
            JOBCNM = f'{chk.chk_name}-完成-短信通知'
            JOBID = chk.chk_done_id + 50000
            JOBPRI = 1
            STGID = 90000
            CHAID = chk.chn_name.chn_id
            JOBCYC = 'D'
            APPURL = SHELL_HOME + ScriptConfig.objects.get(type='90000').script
            # 渠道完成作业参数为空
            PARAM = f'{chk.chk_name}-任务完成'
            JOBVAL = 1
            JOBIGN = 0

            chk_sql5 = eval('f' + '"' + get_sql_stmt('INIT_JOB') + '"')
            curr.execute(chk_sql5)
            # ibm_db.exec_immediate(cur_conn, chk_sql5)

            # 生成渠道完成作业与短信通知作业的依赖关系
            FLWJOB = chk.chk_done_id + 50000
            FLWPRO = chk.chk_done_id

            chk_sql6 = eval('f' + '"' + get_sql_stmt('SCTFLW') + '"')  # 依赖关系：渠道完成作业 -> 短信通知作业
            curr.execute(chk_sql6)
            # ibm_db.exec_immediate(cur_conn, chk_sql6)

            # 执行完成后，将该条记录的新增记录标识为否
            chk.new_record_flag = False
            chk.save()

    ##########################################
    # 处理数据同步卸载任务表
    ##########################################

    sync_task_info = SyncTaskInfo.objects.filter(new_record_flag=True)
    if sync_task_info.exists():
        for sync_task in sync_task_info:
            # 1、先处理数据同步任务

            # InitJob所需字段
            ID = sync_task.sync_id
            JOBTYPE = 1
            JOBCNM = f'数据卸载-{sync_task.chn_name}-{sync_task.tab_name}'
            JOBID = sync_task.sync_id
            JOBPRI = 1
            STGID = 20000
            CHAID = sync_task.chn_name.chn_id
            JOBCYC = 'D'
            APPURL = SHELL_HOME + ScriptConfig.objects.get(type='20000').script
            # 数据卸载类任务参数为数据库名+源系统表名
            PARAM = sync_task.chn_name.db_name + ' ' + sync_task.tab_name
            JOBVAL = 1
            JOBIGN = 0

            # SCTFLW所需字段
            FLWJOB = sync_task.sync_id
            FLWPRO = sync_task.chk_name.chk_id

            # 拼接DB2 SQL语句
            sync_task_sql1 = eval('f' + '"' + get_sql_stmt('INIT_JOB') + '"')
            sync_task_sql2 = eval('f' + '"' + get_sql_stmt('SCTFLW') + '"')  # 依赖关系：检测 -> 卸载

            # 执行DB2 SQL语句
            curr.execute(sync_task_sql1)
            curr.execute(sync_task_sql2)
            # ibm_db.exec_immediate(cur_conn, sync_task_sql1)
            # ibm_db.exec_immediate(cur_conn, sync_task_sql2)

            # 2、 再处理数据装载任务

            # InitJob所需字段
            ID = sync_task.load_id
            JOBTYPE = 1
            JOBCNM = f'数据装载-{sync_task.chn_name}-{sync_task.tab_name}'
            JOBID = sync_task.load_id
            JOBPRI = 1
            STGID = 30000
            CHAID = sync_task.chn_name.chn_id
            JOBCYC = 'D'
            APPURL = SHELL_HOME + ScriptConfig.objects.get(type='30000').script
            # 数据装载类任务参数为数据库名+源系统表名
            PARAM = sync_task.chn_name.db_name + ' ' + sync_task.tab_name
            JOBVAL = 1
            JOBIGN = 0

            # SCTFLW所需字段
            FLWJOB = sync_task.load_id
            FLWPRO = sync_task.sync_id

            # 拼接DB2 SQL语句
            load_task_sql1 = eval('f' + '"' + get_sql_stmt('INIT_JOB') + '"')
            load_task_sql2 = eval('f' + '"' + get_sql_stmt('SCTFLW') + '"')  # 依赖关系：卸载 -> 装载

            # 执行DB2 SQL语句
            curr.execute(load_task_sql1)
            curr.execute(load_task_sql2)
            # ibm_db.exec_immediate(cur_conn, load_task_sql1)
            # ibm_db.exec_immediate(cur_conn, load_task_sql2)

            # 生成装载任务与渠道完成任务依赖关系

            # SCTFLW所需字段
            FLWJOB = sync_task.chk_name.chk_done_id
            FLWPRO = sync_task.load_id

            load_task_sql3 = eval('f' + '"' + get_sql_stmt('SCTFLW') + '"')  # 依赖关系：装载 -> 渠道完成
            curr.execute(load_task_sql3)
            # ibm_db.exec_immediate(cur_conn, load_task_sql3)

            # 执行完成后，将该条记录的新增记录标识为否
            sync_task.new_record_flag = False
            sync_task.save()

    ##########################################
    # 处理数据推送任务表
    ##########################################

    push_task_info = PushTaskInfo.objects.filter(new_record_flag=True)
    if push_task_info.exists():
        for push_task in push_task_info:
            # InitJob所需字段
            ID = push_task.push_id
            JOBTYPE = 1
            JOBCNM = f'数据推送-{push_task.chn_name}-{push_task.push_tab_name}'
            JOBID = push_task.push_id
            JOBPRI = 1
            STGID = 60000
            CHAID = push_task.chn_name.chn_id
            JOBCYC = 'D'
            APPURL = SHELL_HOME + ScriptConfig.objects.get(type='60000').script
            # 数据推送类任务参数为表名
            PARAM = push_task.push_tab_name
            JOBVAL = 1
            JOBIGN = 0

            # SCTFLW所需字段
            FLWJOB = push_task.push_id
            FLWPRO = push_task.source_tab_name.chk_name.chk_done_id

            # 拼接DB2 SQL语句
            push_task_sql1 = eval('f' + '"' + get_sql_stmt('INIT_JOB') + '"')
            push_task_sql2 = eval('f' + '"' + get_sql_stmt('SCTFLW') + '"')  # 依赖关系：渠道完成 -> 推送

            # 执行DB2 SQL语句
            curr.execute(push_task_sql1)
            curr.execute(push_task_sql2)
            # ibm_db.exec_immediate(cur_conn, push_task_sql1)
            # ibm_db.exec_immediate(cur_conn, push_task_sql2)

            # 执行完成后，将该条记录的新增记录标识为否
            push_task.new_record_flag = False
            push_task.save()
