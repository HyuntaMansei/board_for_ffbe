import mysql.connector
import pandas
import pandas as pd
from datetime import date

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
def fetch_data_as_df(sql):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(sql)
    res = cursor.fetchall()
    col_names = cursor.column_names
    cursor.close()
    conn.close()
    df = pd.DataFrame(res, columns=col_names)
    return df
def fetch_data_with_col_names_as_df_with_value(sql, value):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(sql, value)
    res = cursor.fetchall()
    col_names = cursor.column_names
    cursor.close()
    conn.close()
    df = pd.DataFrame(res, columns=col_names)
    return df
def execute_with_values(sql, values=None):
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
    try:
        res = cursor.fetchall()
    except:
        # Nothing to fetch
        res = None
    cursor.close()
    conn.commit()
    conn.close()
    return res
def write_df_to_server(table_name, df_to_write:pd.DataFrame):
    sql_for_col_names = f"""select * from {table_name} LIMIT 1"""
    _, col_names = fetch_data_with_col_names(sql_for_col_names)
    common_col_names = [c for c in col_names if c in df_to_write.columns]
    print(common_col_names)
    str_for_cols = ','.join(common_col_names)
    str_for_vals = ','.join(['%s']*len(common_col_names))
    sql = f"""INSERT INTO {table_name} ({str_for_cols})
    VALUES ({str_for_vals})"""
    print(sql)
    for i, d in df_to_write.iterrows():
        execute_with_values(sql, tuple(d.tolist()))
class BoardManager:
    def __init__(self):
        pass

    def delete_log_in_server(self, ref_date):
        table_to_write = 'guild_battle_log_tb'
        sql_for_delete = f"""DELETE FROM {table_to_write} WHERE match_date = %s"""
        print(sql_for_delete)
        execute_with_values(sql_for_delete, (ref_date,))
    def write_log_to_server(self, df_to_write:pd.DataFrame):
        table_to_write = 'guild_battle_log_tb'
        if not df_to_write.empty:
            sql_for_delete = f"""DELETE FROM {table_to_write} WHERE match_date = %s"""
            execute_with_values(sql_for_delete, (df_to_write['match_date'][0],))
        write_df_to_server(table_to_write, df_to_write)
    def fetch_guild_battle_log(self, ref_date):
        table_to_fetch = 'guild_battle_log_tb'
        sql = f"""SELECT * FROM {table_to_fetch} WHERE match_date = '{ref_date}'"""
        return fetch_data_as_df(sql)
    def fetch_attackers(self, guild_name, ref_date=None):
        latest_date_sql = "SELECT MAX(match_date) AS latest_date FROM opponent_guild_members_tb WHERE guild_name=%s"
        query_value = (guild_name,)
        res = execute_with_values(latest_date_sql, query_value)
        latest_date = None
        for r in res:
            latest_date = r[0]
        print("Latest_date:", latest_date)
        if not latest_date:
            return None
        else:
            value = (guild_name, latest_date)
            sql = f"""select * from opponent_guild_members_tb where guild_name = %s AND match_date=%s"""
            df = fetch_data_with_col_names_as_df_with_value(sql, value)
            df.reset_index(inplace=True)
            return df
    def fetch_defenders(self):
        sql = """select * from guild_members_tb where inuse='y';"""
        data, columns = fetch_data_with_col_names(sql)
        df = pandas.DataFrame(data, columns=columns)
        return df
    def write_attackers(self, attackers:pd.DataFrame=None, t_date=None):
        if t_date == date.today():
            print("Today is the day, writing opponent's guild members.")
            sql = """DELETE FROM opponent_guild_members_tb WHERE match_date = %s"""
            value = (t_date,)
            print(sql)
            print(value)
            execute_with_values(sql, value)
            col_names_to_write = attackers.columns
            cols = ','.join(col_names_to_write)
            val_str = ','.join(['%s']*len(col_names_to_write))
            print(cols)
            print(val_str)
            for i, a in attackers.iterrows():
                sql = f"""INSERT INTO opponent_guild_members_tb ({cols}) 
                VALUES ({val_str})
                """
                print(sql)
                values = tuple(a.tolist())
                execute_with_values(sql, values)
        else:
            pass