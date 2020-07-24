import os
from desire.settings import INTERFACE_DIR
from datacloud.interface.tools import get_db_conn


if __name__ == '__main__':
    # 取数据库游标
    curr = get_db_conn('ETL-Database')
    with open(os.path.join(INTERFACE_DIR, 'initialize.sql'), 'r', encoding='UTF-8') as lines:
        for line in lines:
            curr.execute(line)
