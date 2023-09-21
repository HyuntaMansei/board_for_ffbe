import streamlit as st
import pandas as pd
import numpy as np
import board_manger
from datetime import date
import copy

def write_log(attacker=None, defender=None, stars=None, log=None):
    st.session_state.attack_count += 1
    msg = f"공격 #{st.session_state.attack_count} - 공격자:{attacker}, 방어자:{defender}, 획득별:{stars}"
    log.append(msg)
    new_log = {
        "attack_count":st.session_state.attack_count, "attacker":attacker, "defender":defender, "stars":stars
    }
    st.session_state.df_defence_log = st.session_state.df_defence_log.append(new_log, ignore_index=True)
def write_attackers(attackers_df:pd.DataFrame, guild_name=None):
    columns_to_write = [
        "inuse","guild_name","member_name", 'match_date'
    ]
    attackers_to_write = copy.deepcopy(attackers_df)
    attackers_to_write['inuse'] = 'y'
    attackers_to_write['guild_name'] = guild_name
    if ref_date:
        attackers_to_write['match_date'] = ref_date
        attackers_to_write = attackers_to_write[columns_to_write]
        bm.write_attackers(attackers_to_write, ref_date)
    else:
        attackers_to_write['match_date'] = date.today()
        attackers_to_write = attackers_to_write[columns_to_write]
        bm.write_attackers(attackers_to_write, date.today())
    print(attackers_df)
    print(attackers_to_write)
def fetch_attackers(guild_name, ref_date=None):
    res_df = bm.fetch_attackers(guild_name, ref_date)
    return res_df
def process_logs():
    global defender_board
    df_defence_log = st.session_state.df_defence_log
    for d in defenders['defender_name']:
        defence_count = df_defence_log[df_defence_log['defender'] == d]['stars'].count()
        remaining_stars = 3 - df_defence_log[df_defence_log['defender'] == d]['stars'].sum()
        lost_stars_list = df_defence_log[df_defence_log['defender'] == d]['stars'].tolist()
        lost_starts_1st = lost_stars_list[0] if defence_count > 0 else None
        lost_starts_2nd = lost_stars_list[1] if defence_count > 1 else None
        lost_starts_3rd = lost_stars_list[2] if defence_count > 2 else None
        lost_starts_4th = lost_stars_list[3] if defence_count > 3 else None
        lost_starts_5th = lost_stars_list[4] if defence_count > 4 else None
        new_row = {
            '방횟':defence_count, '잔별':remaining_stars,
            '1방':lost_starts_1st, '2방':lost_starts_2nd, '3방':lost_starts_3rd, '4방':lost_starts_4th, '5방':lost_starts_5th
        }
        defender_board.loc[d] = new_row
    # Alive Attackers
    # New deck
    # 1Attack ali

# session variables
if 'attack_log' not in st.session_state:
    st.session_state.attack_log = []
attack_log = st.session_state.attack_log
if 'attack_count' not in st.session_state:
    st.session_state.attack_count = 0
if 'df_defence_log' not in st.session_state:
    columns = ["attack_count", "attacker", "defender", "stars"]
    st.session_state.df_defence_log = pd.DataFrame(columns=columns)
columns_to_make = ['guild_name', 'member_name']
if 'attackers' not in st.session_state:
    st.session_state.attackers = pd.DataFrame(columns=columns_to_make)
    st.session_state.attackers.reset_index()
# global variables
bm = board_manger.BoardManager()
alive_attackers = []

defenders = bm.fetch_defenders()
columns = ['si','잔별','방횟','1방','2방','3방','4방','5방']
defender_board = pd.DataFrame(columns=columns, index=defenders['defender_name'].tolist())
alive_defenders = []

# Data input
ref_date = st.date_input("기준날짜")
ref_date
st.header("공격자")
opp_guild_name = st.text_input("길드명")

if st.button("공격자 불러오기"):
    st.session_state.attackers = fetch_attackers(guild_name=opp_guild_name,ref_date=ref_date)[columns_to_make]
    st.session_state.attackers.reset_index()
    # attackers = fetch_attackers(guild_name=opp_guild_name)[columns_to_make]
    # st.session_state.attackers.reset_index()
if len(st.session_state.attackers) == 0:
    st.session_state.attackers.loc[0] = {"guild_name":{opp_guild_name}, "member_name":""}
st.session_state.attackers = st.data_editor(st.session_state.attackers, num_rows="dynamic", width=1000, hide_index=True)
if st.button("공격자 저장하기"):
    print("Before: ", st.session_state.attackers)
    st.dataframe(st.session_state.attackers, width=1000)
    write_attackers(attackers_df=st.session_state.attackers, guild_name=opp_guild_name)

# Process logs
process_logs()

# alive_attackers = attackers['member_name'].tolist()
# alive_attackers.sort()
# alive_defenders = defenders['defender_name'].tolist()
# alive_defenders.sort()


attacker = st.selectbox(f"Attacker({len(alive_attackers)})", [""] + alive_attackers)
defender = st.selectbox(f"Defender({len(alive_defenders)})", [""] + alive_defenders)
stars = st.radio("Acq. Stars ", [0, 1, 2, 3])

kwargs = {
    "attacker":attacker,
    "defender":defender,
    "stars":stars,
    "log":attack_log
}
if st.button("입력", on_click=write_log, kwargs=kwargs):
    st.write("Writing Log")
st.session_state.df_defence_log = st.data_editor(st.session_state.df_defence_log, num_rows="dynamic", hide_index=True, width=1000)
if st.button("로그저장"):
    df_to_write = copy.deepcopy(st.session_state.df_defence_log)
    df_to_write['match_date'] = date.today()
    print(f"Columns(saving log): {st.session_state.df_defence_log.columns}")
    bm.write_log_to_server(df_to_write)
if st.button("로그 불러오기"):
    print(f"Columns(Loading log): {st.session_state.df_defence_log.columns}")
    st.session_state.df_defence_log = bm.fetch_guild_battle_log(ref_date)[st.session_state.df_defence_log.columns]
if st.button("로그 초기화"):
    if not st.session_state.df_defence_log.empty:
        st.session_state.df_defence_log = st.session_state.df_defence_log.iloc[0:0]
    bm.delete_log_in_server(ref_date)
col_to_show =['잔별', '방횟', '1방', '2방', '3방']
st.table(defender_board[col_to_show].style.format("{:.0f}"))
attack_log