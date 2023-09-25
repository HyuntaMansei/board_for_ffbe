import streamlit as st
import pandas as pd
import numpy as np
import board_manger
import gsheet_manager
from datetime import date
import copy


# Global variables
cl, cl0, cl1, cl2, cl3 = None, None, None, None, None
bm = None
battle_log_msg = None

col_for_attacker_board = ['남공', '생존', '공횟', '총별', '1공별', '2공별', '1공상대', '2공상대']
col_for_defender_board = ['잔별', '방횟', '1방', '2방', '3방']
columns_for_battle_log = ["attack_count", "attacker", "defender", "stars"]
columns_for_attackers = ['guild_name', 'member_name']

ref_date = None

# Global and Session variables
if 'bm' not in st.session_state:
    st.session_state.bm = board_manger.BoardManager()
bm = st.session_state.bm
if 'battle_log_msg' not in st.session_state:
    st.session_state.battle_log_msg = []
battle_log_msg = st.session_state.battle_log_msg
if 'attack_count' not in st.session_state:
    st.session_state.attack_count = 0
attack_count = st.session_state.attack_count
if 'battle_log_df' not in st.session_state:
    st.session_state.battle_log_df = pd.DataFrame(columns=columns_for_battle_log)
    st.session_state.battle_log_df.reset_index(inplace = True, drop = True)
battle_log_df = st.session_state.battle_log_df
if 'attackers' not in st.session_state:
    st.session_state.attackers = pd.DataFrame(columns=columns_for_attackers)
    st.session_state.attackers.reset_index(inplace=True, drop=True)
attackers = st.session_state.attackers
if 'defenders' not in st.session_state:
    st.session_state.defenders = bm.fetch_defenders()
defenders = st.session_state.defenders
if 'opp_guild_name' not in st.session_state:
    st.session_state.opp_guild_name = None
opp_guild_name = st.session_state.opp_guild_name
if 'attacker_board' not in st.session_state:
    st.session_state.attacker_board = pd.DataFrame(columns=col_for_attacker_board, index=attackers['member_name'].tolist())
    st.session_state.attacker_board['남공'] = 2
    st.session_state.attacker_board['생존'] = True
attacker_board = st.session_state.attacker_board
if not len(attacker_board):
    attacker_board = pd.DataFrame(columns=col_for_attacker_board,
                                                   index=attackers['member_name'].tolist())
    attacker_board['남공'] = 2
    attacker_board['생존'] = True
if 'defender_board' not in st.session_state:
    st.session_state.defender_board = pd.DataFrame(columns=col_for_defender_board, index=defenders['defender_name'].tolist())
defender_board = st.session_state.defender_board
if 'alive_attackers' not in st.session_state:
    st.session_state.alive_attackers = []
alive_attackers = st.session_state.alive_attackers
if 'alive_defenders' not in st.session_state:
    st.session_state.alive_defenders = []
alive_defenders = st.session_state.alive_defenders
new_attackers = None
def centered_header(header_text, cv=None):
    if not cv:
        cv = st
    # Use HTML to center-align the header
    cv.markdown(f"<h1 style='text-align: center;'>{header_text}</h1>", unsafe_allow_html=True)
def divide_screen_as_default():
    global cl, cl0, cl1, cl2, cl3
    cl = divide_screen(3)
    cl0, cl1, cl2, cl3 = cl[0], cl[1], cl[2], cl[0]
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
def divide_screen_by_2():
    global cl, cl0, cl1, cl2, cl3
    cl = divide_screen(2)
    cl0, cl1, cl2, cl3 = cl[0], cl[1], cl[0], cl[1]
def divide_screen_by_3():
    global cl, cl0, cl1, cl2, cl3
    cl = divide_screen(3)
    cl0, cl1, cl2, cl3 = cl[0], cl[1], cl[2], cl[0]
def divide_screen_by_4():
    global cl, cl0, cl1, cl2, cl3
    cl = divide_screen(4)
    cl0, cl1, cl2, cl3 = cl[0], cl[1], cl[2], cl[3]
def write_log(attacker=None, defender=None, stars=None):
    st.session_state.attack_count += 1
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
    global bm, defenders, alive_attackers, alive_defenders, attacker_board, defender_board, ref_date, opp_guild_name, battle_log_msg
    # Defender Board
    # print("In precoss log, ")
    # print(defenders)
    # print(attackers)
    # print(defender_board)
    # print(attacker_board)

    for d in defenders['defender_name']:
        defence_count = int(battle_log_df[battle_log_df['defender'] == d]['stars'].count())
        remain_stars = int(3 - battle_log_df[battle_log_df['defender'] == d]['stars'].sum())
        lost_stars_list = battle_log_df[battle_log_df['defender'] == d]['stars'].tolist()
        lost_starts_1st = int(lost_stars_list[0]) if defence_count > 0 else None
        lost_starts_2nd = int(lost_stars_list[1]) if defence_count > 1 else None
        lost_starts_3rd = int(lost_stars_list[2]) if defence_count > 2 else None
        lost_starts_4th = int(lost_stars_list[3]) if defence_count > 3 else None
        lost_starts_5th = int(lost_stars_list[4]) if defence_count > 4 else None
        new_row = {
            '방횟':defence_count, '잔별':remain_stars,
            '1방':lost_starts_1st, '2방':lost_starts_2nd, '3방':lost_starts_3rd, '4방':lost_starts_4th, '5방':lost_starts_5th
        }
        defender_board.loc[d] = new_row
    st.session_state.defender_board = defender_board
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
    # print(battle_log_df)
    st.session_state.attacker_board = attacker_board
    # Log messages
    st.session_state.battle_log_msg = pd.DataFrame(columns=["attack_count","공격자", "방어자", "획득별"])
    st.session_state.battle_log_msg.set_index("attack_count", inplace=True)
    for i, l in battle_log_df.iterrows():
        attack_count = l['attack_count']
        attacker = l['attacker']
        defender = l['defender']
        stars = l['stars']
        st.session_state.battle_log_msg.loc[attack_count] = {"공격자":attacker, "방어자":defender, "획득별":stars}
    # Alive Attackers&Defenders
    indexer_alive_attackers = attacker_board['남공'] > 0
    indexer_alive_defenders = defender_board['잔별'] > 0
    alive_attackers = list(attacker_board[indexer_alive_attackers].index)
    alive_defenders = list(defender_board[indexer_alive_defenders].index)
    try:
        alive_attackers.sort()
        alive_defenders.sort()
    except Exception as e:
        print(e)
def write_to_sheet():
    gm = gsheet_manager.sheet_manager_for_ffbe()
    gm.open_sheets()
    # sheets to write = log, attacker_board, defender_board
    gm.update_sheet_with_df_including_index('log', battle_log_df)
    gm.update_sheet_with_df_including_index('attacker_board', attacker_board)
    gm.update_sheet_with_df_including_index('defender_board', defender_board)
def display_board():
    global ally_point, ally_remaining_attacks, opp_member_count
    # Create a number input for integers
    divide_screen_as_default()

    # Opponent's Calculation
    # print(attacker_board)
    opp_point = attacker_board['총별'].sum()
    opp_remaining_attacks = opp_member_count * 2 - attacker_board['공횟'].sum()

    # Point Board
    divide_screen_as_default()
    centered_header("상황판", cl1)
    divide_screen_as_default()
    centered_header("WA", cl0)
    centered_header("VS.", cl1)
    cl2.header(opp_guild_name)

    divide_screen_as_default()
    centered_header("점수", cl1)
    centered_header(ally_point, cl0)
    centered_header(opp_point, cl2)

    centered_header("남은공격", cl1)
    centered_header(ally_remaining_attacks, cl0)
    centered_header(opp_remaining_attacks, cl2)

    ally_avg = round(ally_point / (60 - ally_remaining_attacks), 2)
    try:
        opp_avg = round(opp_point / (60 - opp_remaining_attacks), 2)
    except:
        opp_avg = 0
    centered_header("평균", cl1)
    centered_header(ally_avg, cl0)
    centered_header(opp_avg, cl2)

    centered_header("방어판")
    dboard_sorted = defender_board.sort_values(by=['잔별', '방횟'], ascending=[False, False])
    dboard_to_show = dboard_sorted.applymap(lambda x: '' if pd.isna(x) else '{:.0f}'.format(x))

    unattacked_decks_to_show = dboard_to_show[dboard_sorted['방횟']==0]
    three_star_decks_to_show = dboard_to_show[(dboard_sorted['방횟']!=0) & (dboard_sorted['잔별']==3)]
    two_star_decks_to_show = dboard_to_show[(dboard_sorted['방횟']!=0) & (dboard_sorted['잔별']==2)]
    one_star_decks_to_show = dboard_to_show[(dboard_sorted['방횟']!=0) & (dboard_sorted['잔별']==1)]
    no_star_decks_to_show = dboard_to_show[(dboard_sorted['방횟']!=0) & (dboard_sorted['잔별']==0)]
    st.subheader(f"새삥덱 - {len(unattacked_decks_to_show)}" )
    st.subheader(list(unattacked_decks_to_show.index))
    st.subheader(f"3잔별 - {len(three_star_decks_to_show)}" )
    st.table(three_star_decks_to_show)
    st.subheader(f"2잔별 - {len(two_star_decks_to_show)}" )
    st.table(two_star_decks_to_show)
    st.subheader(f"1잔별 - {len(one_star_decks_to_show)}" )
    st.table(one_star_decks_to_show)
    st.subheader(f"마감덱 - {len(no_star_decks_to_show)}" )
    st.table(no_star_decks_to_show)

    centered_header("공격판")
    aboard_to_show = attacker_board.sort_values(by=['남공', '총별'], ascending=[False, False])

    new_deck_to_show = list(aboard_to_show[aboard_to_show['남공'] == 2].index)
    st.subheader(f"공격전(새삥) - {len(new_deck_to_show)}")
    st.subheader(new_deck_to_show)

    remain_1_deck_to_show = aboard_to_show[aboard_to_show['남공'] == 1].fillna('')
    st.subheader(f"1공 후 대기 - {len(remain_1_deck_to_show)}")
    # st.table(remain_1_deck_to_show)
    st.table(remain_1_deck_to_show[["1공별", "1공상대"]])

    fin_deck_to_show = aboard_to_show[(aboard_to_show['남공'] == 0) & (aboard_to_show['생존'] == True)].fillna('')
    st.subheader(f"2공 성공 - {len(fin_deck_to_show)}")
    st.table(fin_deck_to_show[["총별", '1공별', '2공별', '1공상대', '2공상대']])

    fail_2_deck_to_show = aboard_to_show[(aboard_to_show['공횟'] == 2) & (aboard_to_show['생존'] == False)].fillna('')
    st.subheader(f"2공 실패 - {len(fail_2_deck_to_show)}")
    st.table(fail_2_deck_to_show[["총별", '1공별', '2공별', '1공상대', '2공상대']])

    fail_1_deck_to_show = aboard_to_show[(aboard_to_show['공횟'] == 1) & (aboard_to_show['생존'] == False)].fillna('')
    st.subheader(f"1공 실패 - {len(fail_1_deck_to_show)}")
    st.table(fail_1_deck_to_show[['1공별', '1공상대']])

    st.header("로그")
    st.table(st.session_state.battle_log_msg)
def setting_page():
    global bm, defenders, alive_attackers, alive_defenders, attacker_board, defender_board, ref_date, opp_guild_name, new_attackers
    # Screen setting
    st.header(f"공격자 ({len(st.session_state.attackers)})")
    st.session_state.attackers.reset_index(inplace=True, drop=True)
    new_attackers = st.data_editor(st.session_state.attackers, num_rows="dynamic", width=1000, hide_index=True)
    divide_screen_as_default()
    try:
        cl0.text(f"# of attackers: {len(new_attackers)}")
    except:
        pass
    if cl1.button("공격자 불러오기"):
        res_df = fetch_attackers(guild_name=opp_guild_name, ref_date=ref_date)
        if res_df is not None:
            st.session_state.attackers = res_df[columns_for_attackers]
            if not opp_guild_name:
                st.session_state.opp_guild_name = res_df['guild_name'].iloc[0]
        else:
            st.session_state.attackers = pd.DataFrame(columns=columns_for_attackers)
        st.session_state.attackers.reset_index(inplace=True, drop=True)
    if cl2.button("공격자 저장하기"):
        write_attackers(attackers_df=new_attackers, guild_name=opp_guild_name)
        st.session_state.attackers = new_attackers
        try:
            st.subheader(f"{len(st.session_state.attackers['member_name'].tolist())} names Saved.")
            st.write(f"Saved names: {st.session_state.attackers['member_name'].tolist()}")
        except:
            pass
    divide_screen_as_default()
    new_battle_log_df = st.data_editor(st.session_state.battle_log_df, num_rows="dynamic", hide_index=True,
                                        width=1000)
    divide_screen_as_default()

    if cl0.button("로그 저장"):
        new_battle_log_df['match_date'] = date.today()
        new_battle_log_df.sort_values(by='attack_count', inplace=True)
        new_battle_log_df.reset_index(drop=True, inplace=True)
        bm.write_log_to_server(new_battle_log_df)
        st.session_state.battle_log_df = new_battle_log_df
    if cl1.button("로그 불러오기"):
        loaded_df = bm.fetch_guild_battle_log(ref_date)[columns_for_battle_log]
        st.session_state.battle_log_df = loaded_df.reset_index(drop=True)
        st.session_state.attack_count = st.session_state.battle_log_df['attack_count'].iloc[-1]
    if cl2.button("로그 초기화"):
        if not st.session_state.battle_log_df.empty:
            st.session_state.battle_log_df = st.session_state.battle_log_df.iloc[0:0]
            st.session_state.battle_log_df.reset_index(drop=True, inplace=True)
        bm.delete_log_in_server(ref_date)
def preprocessor():
    global bm, defenders, alive_attackers, alive_defenders, attacker_board, defender_board, ref_date, opp_guild_name
    print(f"before.\n {attacker_board.dtypes}")
    # attacker_board['남공'] = attacker_board['남공'].astype(int)
    # attacker_board['남공'] = attacker_board['남공'].applymap(lambda x: int(x))
    attacker_board = attacker_board.applymap(lambda x: int(x) if type(x) == np.int64 else x)
    print(f"after.\n {attacker_board.dtypes}")
    process_logs()
def postprocessor():
    st.session_state.alive_attackers = alive_attackers
    st.session_state.alive_defenders = alive_defenders

if __name__ == '__main__':
    # Preprocessor
    preprocessor()
    # Create a sidebar with options to navigate between pages
    page = st.sidebar.selectbox("Select a page", ["Setting", "Display"])
    # Sidebar
    with st.sidebar:
        ref_date = st.date_input("기준날짜")
        if opp_guild_name:
            opp_guild_name = st.text_input("길드이름", opp_guild_name)
        else:
            opp_guild_name = st.text_input("길드이름")
        st.subheader(f"로그 기록 - {st.session_state.attack_count}")
        attacker = st.selectbox(f"Attacker({len(alive_attackers)})", [""] + alive_attackers)
        defender = st.selectbox(f"Defender({len(alive_defenders)})", [""] + alive_defenders)
        remaining_stars = int(defender_board.loc[defender]['잔별']) if defender else 3
        sb_cl = st.columns(2)
        sb_cl0 = sb_cl[0]
        sb_cl1 = sb_cl[1]
        stars = sb_cl0.radio("Acq. Stars ", [0, 1, 2, 3], index=remaining_stars)
        if sb_cl1.button("로그 입력"):
            write_log(attacker=attacker, defender=defender, stars=stars)
            process_logs()
        sb_cl1.button("Refresh")
        if sb_cl1.button("WriteToSheet"):
            write_to_sheet()
        ally_point = int(sb_cl0.number_input("WA획득점수:", value=0, step=1, format="%d"))
        ally_remaining_attacks = int(sb_cl0.number_input("WA남은공격:", value=0, step=1, format="%d"))
        opp_member_count = int(sb_cl0.number_input("상대인원:", value=30, step=1, format="%d"))
    # Display the selected page
    if page == "Setting":
        setting_page()
    elif page == "Display":
        display_board()
    postprocessor()
