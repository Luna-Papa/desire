import os
from django.core.wsgi import get_wsgi_application
import ibm_db
from datacloud.interface.tools import get_db_conn, get_sql_stmt
from datetime import datetime

# 加载django项目环境参数
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "desire.settings")
application = get_wsgi_application()

from datacloud.models import ChannelInfo, ChkInfo, SyncTaskInfo, PushTaskInfo, ScriptConfig

if __name__ == '__main__':
    """
    前端配置表中检测任务、同步加载任务或者推送任务置为无效时，
    在后端ETL调度表进行变更的处理过程。
    """

    # 取数据库游标
    curr = get_db_conn('ETL-Database')

    ##########################################
    # 处理渠道配置表
    ##########################################
    """
    新增渠道则渠道一直存在，不存在无效状态。因此ChannelInfo表不需要处理。
    """

    # 获取当天日期，用于筛选记录
    today = datetime.today()

    ##########################################
    # 处理渠道检测表
    ##########################################

    check_info = ChkInfo.objects.filter(val_flag=False, updated_time__date=today)
    if check_info.exists():
        for check in check_info:
            JOBID = check.chk_id
            sql_stmt_check = eval('f' + '"' + get_sql_stmt('SCTJOB') + '"')
            curr.execute(sql_stmt_check)
            # ibm_db.exec_immediate(cur_conn, sql_stmt_check)

            # 处理关联的同步任务，将其状态标识置为无效，并更新其最后修改时间为当前时点
            check_name = check.chk_name
            related_sync_info = SyncTaskInfo.objects.filter(check_name=check_name)
            if related_sync_info.exists():
                for sync in related_sync_info:
                    sync.val_flag = False
                    sync.updated_time = datetime.now()
                    sync.save()
                    # 处理同步任务关联的推送任务
                    source_tab_name = sync.tab_name
                    related_push_info = PushTaskInfo.objects.filter(source_tab_name=source_tab_name)
                    if related_push_info.exists():
                        for push in related_push_info:
                            push.val_flag = False
                            push.updated_time = datetime.now()
                            push.save()

    ##########################################
    # 处理同步装载任务表
    ##########################################

    sync_info = SyncTaskInfo.objects.filter(val_flag=False, updated_time__date=today)
    if sync_info.exists():
        for sync in sync_info:
            # 需要同时将卸载任务和装载任务都置为无效
            JOBID = sync.sync_id
            sql_stmt = eval('f' + '"' + get_sql_stmt('SCTJOB') + '"')
            curr.execute(sql_stmt)
            # ibm_db.exec_immediate(cur_conn, sql_stmt)
            JOBID = sync.load_id
            sql_stmt_sync = eval('f' + '"' + get_sql_stmt('SCTJOB') + '"')
            curr.execute(sql_stmt_sync)
            # ibm_db.exec_immediate(cur_conn, sql_stmt_sync)

            # 处理关联的推送任务，将其状态标识置为无效，并更新其最后修改时间为当前时点
            source_tab_name = sync.tab_name
            related_push_info = PushTaskInfo.objects.filter(source_tab_name=source_tab_name)
            if related_push_info.exists():
                for push in related_push_info:
                    push.val_flag = False
                    push.updated_time = datetime.now()
                    push.save()
                # 推送任务的处理全部放在下一部分逻辑

    ##########################################
    # 处理推送任务表
    ##########################################

    push_info = PushTaskInfo.objects.filter(val_flag=False, created_time__date=today)
    if push_info.exists():
        for push in push_info:
            JOBID = push.push_id
            sql_stmt_sync_push = eval('f' + '"' + get_sql_stmt('SCTJOB') + '"')
            curr.execute(sql_stmt_sync_push)
            # ibm_db.exec_immediate(cur_conn, sql_stmt_sync_push)
