import ibm_db


class Dd2ExecuteSQL:

    def __init__(self, conn_str):
        try:
            self.conn = ibm_db.connect(conn_str, "", "")
        except:
            print("no connection: ", ibm_db.conn_errormsg())
        else:
            print("ETL-DB connection was successful.")

    def execute(self, sql):
        try:
            stmt = ibm_db.exec_immediate(self.conn, sql)
        except:
            print(f"{sql} execute failed: ", ibm_db.stmt_errormsg())

    def close_connection(self):
        ibm_db.close(self.conn)
