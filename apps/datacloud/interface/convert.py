from .DB2 import Dd2ExecuteSQL


def convert(sql1, sql2):
    pre = Dd2ExecuteSQL()
    try:
        pre.execute(sql1)
    except Exception as ex:
        print(ex)
    finally:
        pre.execute(sql2)
        pre.close_connection()
        return True
