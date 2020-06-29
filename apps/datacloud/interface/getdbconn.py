import configparser
import os
from desire.settings import INTERFACE_DIR


def db_conn(db):
    cf = configparser.ConfigParser()
    # cf.read(BASE_DIR + os.sep + 'apps' + os.sep + 'datacloud' + os.sep + 'interface' + os.sep + 'dbconf.ini')
    cf.read(os.path.join(INTERFACE_DIR, 'dbconf.ini'))
    # secs = cf.sections()
    host = cf.get(db, "host")
    database = cf.get(db, "db")
    port = cf.get(db, "port")
    user = cf.get(db, "user")
    password = cf.get(db, "password")
    conn_str = f"DATABASE={database};HOSTNAME='{host}';PORT={port};PROTOCOL=TCPIP;UID={user};PWD={password};"
    return conn_str


