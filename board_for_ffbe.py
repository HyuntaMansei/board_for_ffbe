import streamlit as st
import pandas as pd
import numpy as np
import board_manger
from datetime import date
import copy

# Define the function for Page 1
def page1():
    st.title("Page 1")
    st.write("This is Page 1")

# Define the function for Page 2
def display_board():
    st.title("Page 2")
    st.write("This is Page 2")

# Global variables
cl, cl0, cl1, cl2, cl3 = None, None, None, None, None
bm = None

# Attackers는 세션변수로
defenders = None
alive_attackers = []
alive_defenders = []

attacker_board = None
col_for_attacker_board = ['남공', '생존', '공횟', '총별', '1공별', '2공별', '1공상대', '2공상대']
defender_board = None
col_for_defender_board = ['잔별', '방횟', '1방', '2방', '3방']

ref_date = None
opp_guild_name = None

def main():
    global bm, defenders, alive_attackers, alive_defenders, attacker_board, defender_board, ref_date, opp_guild_name
    # Screen setting
    divide_screen_of_4()
    # session variables
    if 'attack_log' not in st.session_state:
        st.session_state.attack_log = []
    attack_log = st.session_state.attack_log
    if 'attack_count' not in st.session_state:
        st.session_state.attack_count = 0
    columns_for_battle_log = ["attack_count", "attacker", "defender", "stars"]
    if 'battle_log_df' not in st.session_state:
        st.session_state.battle_log_df = pd.DataFrame(columns=columns_for_battle_log)
    columns_for_attackers = ['guild_name', 'member_name']
    if 'attackers' not in st.session_state:
        st.session_state.attackers = pd.DataFrame(columns=columns_for_attackers)
        st.session_state.attackers.reset_index(inplace=True)
    # global variables
    bm = board_manger.BoardManager()

    attacker_board = pd.DataFrame(columns=col_for_attacker_board, index=st.session_state.attackers['member_name'].tolist())
    attacker_board['남공'] = 2
    attacker_board['생존'] = True

    defenders = bm.fetch_defenders()
    columns_for_defender_board = ['si', '잔별', '방횟', '1방', '2방', '3방', '4방', '5방']
    defender_board = pd.DataFrame(columns=columns_for_defender_board, index=defenders['defender_name'].tolist())

    ref_date = st.date_input("기준날짜")
    st.header("공격자")
    opp_guild_name = st.text_input("길드이름")
    divide_screen_of_4()
    # Data input
    if cl2.button("공격자 불러오기"):
        res_df = fetch_attackers(guild_name=opp_guild_name, ref_date=ref_date)
        if res_df is not None:
            st.session_state.attackers = res_df[columns_for_attackers]
        else:
            st.session_state.attackers = pd.DataFrame(columns=columns_for_attackers)
        st.session_state.attackers.reset_index(inplace=True)
    new_attackers = st.data_editor(st.session_state.attackers, num_rows="dynamic", width=1000, hide_index=True)

    if cl3.button("공격자 저장하기"):
        write_attackers(attackers_df=new_attackers, guild_name=opp_guild_name)
        st.session_state.attackers = new_attackers
        st.dataframe(st.session_state.attackers, width=1000)

    process_logs()
    # Alive Attackers&Defenders
    indexer_alive_attackers = attacker_board['남공'] > 0
    indexer_alive_defenders = defender_board['잔별'] > 0
    alive_attackers = list(attacker_board[indexer_alive_attackers].index)
    alive_defenders = list(defender_board[indexer_alive_defenders].index)
    alive_attackers.sort()
    alive_defenders.sort()

    st.header("로그 기록")
    divide_screen_of_4()
    attacker = cl0.selectbox(f"Attacker({len(alive_attackers)})", [""] + alive_attackers)
    defender = cl1.selectbox(f"Defender({len(alive_defenders)})", [""] + alive_defenders)
    stars = cl2.radio("Acq. Stars ", [0, 1, 2, 3])
    new_battle_log_df = st.data_editor(st.session_state.battle_log_df, num_rows="dynamic", hide_index=True,
                                        width=1000)
    kwargs = {
        "attacker": attacker,
        "defender": defender,
        "stars": stars,
        "log": attack_log
    }
    if cl3.button("로그 입력", on_click=write_log, kwargs=kwargs):
        pass
    divide_screen_of_4()

    if cl0.button(" 로그 입력 ", on_click=write_log, kwargs=kwargs):
        pass
    if cl1.button("로그 저장"):
        new_battle_log_df['match_date'] = date.today()
        bm.write_log_to_server(new_battle_log_df)
        st.session_state.battle_log_df = new_battle_log_df
    if cl2.button("로그 불러오기"):
        st.session_state.battle_log_df = bm.fetch_guild_battle_log(ref_date)[st.session_state.battle_log_df.columns]
    if cl3.button("로그 초기화"):
        if not st.session_state.battle_log_df.empty:
            st.session_state.battle_log_df = st.session_state.battle_log_df.iloc[0:0]
        bm.delete_log_in_server(ref_date)

    divide_screen_of_4()
    cl0.header("공격판")
    cl3.radio("Refresh", [" ", " "])
    # st.table(attacker_board[col_for_attacker_board].style.format("{:.0f}"))
    st.table(attacker_board)
    st.header("방어판")
    st.table(defender_board[col_for_defender_board].style.format("{:.0f}"))
    attack_log

def divide_screen(col_num:float):
    r = (1/col_num)*100
    st.write(f'''<style>
    [data-testid="column"] {{
        width: calc({r}% - 1rem) !important;
        flex: 1 1 calc({r}% - 1rem) !important;
        min-width: calc({r}% - 1rem) !important;
    }}
    </style>''', unsafe_allow_html=True)
    return st.columns(col_num)
def divide_screen_of_4():
    global cl, cl0, cl1, cl2, cl3, cl4
    cl = divide_screen(4)
    cl0, cl1, cl2, cl3 = cl[0], cl[1], cl[2], cl[3]
def write_log(attacker=None, defender=None, stars=None, log=None):
    st.session_state.attack_count += 1
    msg = f"공격 #{st.session_state.attack_count} - 공격자:{attacker}, 방어자:{defender}, 획득별:{stars}"
    log.append(msg)
    new_log = {
        "attack_count":st.session_state.attack_count, "attacker":attacker, "defender":defender, "stars":stars
    }
    st.session_state.battle_log_df = st.session_state.battle_log_df.append(new_log, ignore_index=True)
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
def fetch_attackers(guild_name, ref_date=None):
    res_df = bm.fetch_attackers(guild_name, ref_date)
    return res_df
def process_logs():
    battle_log_df = st.session_state.battle_log_df
    global alive_attackers, alive_defenders
    # Defender Board
    for d in defenders['defender_name']:
        defence_count = battle_log_df[battle_log_df['defender'] == d]['stars'].count()
        remaining_stars = 3 - battle_log_df[battle_log_df['defender'] == d]['stars'].sum()
        lost_stars_list = battle_log_df[battle_log_df['defender'] == d]['stars'].tolist()
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
    # Attacker Board
    battle_log_df.sort_values(by="attack_count", ascending=True, inplace=True)
    for i, log in battle_log_df.iterrows():
        attacker = log['attacker']
        defender = log['defender']
        stars = log['stars']

        prev_battle_log_for_defender = battle_log_df.iloc[0:i]
        prev_battle_log_for_defender = prev_battle_log_for_defender[prev_battle_log_for_defender['defender']==defender]

        prev_battle_log_for_attacker = battle_log_df.iloc[0:i]
        prev_battle_log_for_attacker = prev_battle_log_for_attacker[prev_battle_log_for_attacker['attacker']==attacker]

        stars_before_attack = prev_battle_log_for_defender['stars'].sum()
        survival = True if stars_before_attack + stars >= 3 else False
        attack_count = len(prev_battle_log_for_attacker) + 1
        remaining_attack_count = 1 if survival and (attack_count<=1) else 0
        if len(prev_battle_log_for_attacker):
            print(prev_battle_log_for_attacker)
            first_ac_stars = prev_battle_log_for_attacker['stars'].iloc[0]
            first_attack_defender = prev_battle_log_for_attacker['defender'].iloc[0]
            second_ac_stars = stars
            second_attack_defender = defender
            total_stars = first_ac_stars + second_ac_stars
        else:
            first_ac_stars = stars
            first_attack_defender = defender
            second_ac_stars = None
            second_attack_defender = None
            total_stars = first_ac_stars
        new_row = {
            '남공':remaining_attack_count, '생존':survival, '공횟':attack_count, '총별':total_stars, '1공별':first_ac_stars, '2공별':second_ac_stars, '1공상대':first_attack_defender, '2공상대':second_attack_defender
        }
        attacker_board.loc[attacker] = new_row


    # New deck
    # 1Attack ali

if __name__ == '__main__':
    # Create a sidebar with options to navigate between pages
    page = st.sidebar.selectbox("Select a page", ["Page 1", "Page 2"])

    # Display the selected page
    if page == "Page 1":
        main()
    elif page == "Page 2":
        display_board()