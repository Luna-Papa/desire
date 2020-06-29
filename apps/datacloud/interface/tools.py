import configparser
import os
from desire.settings import INTERFACE_DIR


def get_db_conn(db):
    cf = configparser.ConfigParser()
    cf.read(os.path.join(INTERFACE_DIR, 'dbconf.ini'))
    # secs = cf.sections()
    host = cf.get(db, "host")
    database = cf.get(db, "db")
    port = cf.get(db, "port")
    user = cf.get(db, "user")
    password = cf.get(db, "password")
    conn_str = f"DATABASE={database};HOSTNAME='{host}';PORT={port};PROTOCOL=TCPIP;UID={user};PWD={password};"
    return conn_str


def get_sql_stmt(table):
    cf = configparser.ConfigParser()
    cf.read(os.path.join(INTERFACE_DIR, 'etl_convert_sql.ini'))
    # secs = cf.sections()
    stmt = cf.get(table, "SQL")
    return stmt



