import configparser
import os
from desire.settings import INTERFACE_DIR
import ibm_db_dbi


def get_db_conn(db):
    cf = configparser.ConfigParser()
    cf.read(os.path.join(INTERFACE_DIR, 'conf', 'dbconf.ini'))
    # secs = cf.sections()
    host = cf.get(db, "host")
    database = cf.get(db, "db")
    port = cf.get(db, "port")
    user = cf.get(db, "user")
    password = cf.get(db, "password")
    # 生成数据库连接配置
    conn = ibm_db_dbi.connect(f"PORT={port};PROTOCOL=TCPIP;", host=f"{host}", user=f"{user}",
                                   password=f"{password}", database=f"{database}")
    conn.set_autocommit(True)
    curr = conn.cursor()
    # 返回游标
    return curr


def get_sql_stmt(table):
    cf = configparser.ConfigParser()
    cf.read(os.path.join(INTERFACE_DIR, 'conf', 'etl_convert_sql.ini'))
    # secs = cf.sections()
    stmt = cf.get(table, "SQL")
    return stmt



