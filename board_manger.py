import mysql.connector
import pandas
import pandas as pd

def connect_db():
    db_connection = mysql.connector.connect(
    host='146.56.43.43',
    user='ffbemaster',
    password='aksaksgo1!',
    database='ffbe'
    )
    return db_connection
def fetch_data(sql):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(sql)
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res
def fetch_data_with_col_names(sql):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(sql)
    res = cursor.fetchall()
    col_names = cursor.column_names
    cursor.close()
    conn.close()
    return res, col_names
def write_to_server(sql, values=None):
    conn = connect_db()
    cursor = conn.cursor()
    if values == None:
        cursor.execute(sql)
    else:
        if type(values) != list:
            cursor.execute(sql, values)
        else:
            for i in range(len(values)):
                cursor.execute(sql, values[i])
    res = cursor.fetchall()
    cursor.close()
    conn.commit()
    conn.close()
    return res

class BoardManager:
    def __init__(self):
        pass
    def fetch_attackers(self):
        return [
            "riamo",
            "aellan",
            "kingd",
            "adem",
            "nidhogg"
        ]
    def fetch_defenders(self):
        conn = connect_db()
        sql = """select * from guild_members_tb where inuse='y';"""
        data, columns = fetch_data_with_col_names(sql)
        df = pandas.DataFrame(data, columns=columns)
        return df