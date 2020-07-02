import os
from django.core.wsgi import get_wsgi_application
from datetime import datetime
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
    db_conn = get_db_conn('ETL-Database')
    # cur_conn = ibm_db.connect(db_conn, "", "")

    ##########################################
    # 处理渠道配置表
    ##########################################
    """
    新增渠道则渠道一直存在，不存在无效状态。因此ChannelInfo表不需要处理。
    """

    # 获取当天日期，用于筛选记录
    today = datetime.now().strftime('%Y-%m-%d')
    ##########################################
    # 处理渠道检测表
    ##########################################

    if ChkInfo.updated_time.strftime('%Y-%m-%d') == today and ChkInfo.val_flag == False:
        pass



