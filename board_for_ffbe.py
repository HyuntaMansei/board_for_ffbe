import streamlit as st
import pandas as pd
import numpy as np
import board_manger

def write_log(attacker=None, defender=None, stars=None, log=None):
    st.session_state.attack_count += 1
    global df_log
    msg = f"공격 #{st.session_state.attack_count} - 공격자:{attacker}, 방어자:{defender}, 획득별:{stars}"
    log.append(msg)
    new_log = {
        "count":st.session_state.attack_count, "attacker":attacker, "defender":defender, "stars":stars
    }
    st.session_state.df_log = df_log.append(new_log, ignore_index=True)
    df_log = st.session_state.df_log
    print(df_log)

def process_logs():
    global df_defenders
    for d in defenders['defender_name']:
    # d = "티파록하트"
        defence_count = df_log[df_log['defender']==d]['stars'].count()
        remaining_stars = 3 - df_log[df_log['defender']==d]['stars'].sum()
        lost_stars_list = df_log[df_log['defender']==d]['stars'].tolist()
        lost_starts_1st = lost_stars_list[0] if defence_count > 0 else None
        lost_starts_2nd = lost_stars_list[1] if defence_count > 1 else None
        lost_starts_3rd = lost_stars_list[2] if defence_count > 2 else None
        lost_starts_4th = lost_stars_list[3] if defence_count > 3 else None
        lost_starts_5th = lost_stars_list[4] if defence_count > 4 else None
        new_row = {
            '방횟':defence_count, '잔별':remaining_stars,
            '1방':lost_starts_1st, '2방':lost_starts_2nd, '3방':lost_starts_3rd, '4방':lost_starts_4th, '5방':lost_starts_5th
        }
        df_defenders.loc[d] = new_row

if 'log' not in st.session_state:
    st.session_state.log = []
log = st.session_state.log
if 'attack_count' not in st.session_state:
    st.session_state.attack_count = 0
if 'df_log' not in st.session_state:
    columns = ["count", "attacker", "defender", "stars"]
    st.session_state.df_log = pd.DataFrame(columns=columns)
df_log = st.session_state.df_log

#global variables
bm = board_manger.BoardManager()
attackers = bm.fetch_attackers()
defenders = bm.fetch_defenders()
print("AA")
print(defenders)
columns = ['si','잔별','방횟','1방','2방','3방','4방','5방']
df_defenders = pd.DataFrame(columns=columns, index=defenders['defender_name'].tolist())
print(df_defenders)
# df_defenders = pd.DataFrame(columns=columns, index=defenders['defender_name'].tolist())

# Process logs
process_logs()

alive_attackers = attackers
alive_attackers.sort()
alive_defenders = defenders['defender_name'].tolist()
alive_defenders.sort()

attacker = st.selectbox("Attacker", [""] + alive_attackers)
defender = st.selectbox("Defender", [""] + alive_defenders)
stars = st.radio("Acq. Stars ", [0, 1, 2, 3])

kwargs = {
    "attacker":attacker,
    "defender":defender,
    "stars":stars,
    "log":log
}

if st.button("입력", on_click=write_log, kwargs=kwargs):
    st.write("Writing Log")

st.session_state.df_log = st.experimental_data_editor(df_log, num_rows="dynamic")
df_log = st.session_state.df_log
col_to_show =['잔별', '방횟', '1방', '2방', '3방']
df_defenders[col_to_show]
log