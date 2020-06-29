import os
from desire.settings import INTERFACE_DIR
from datacloud.interface.tools import get_db_conn
import ibm_db

if __name__ == '__main__':
    db_conn = get_db_conn('ETL-Database')
    cur_conn = ibm_db.connect(db_conn, "", "")
    with open(os.path.join(INTERFACE_DIR, 'etl_initialize.sql'), 'r', encoding='UTF-8') as lines:
        for line in lines:
            ibm_db.exec_immediate(cur_conn, line)
