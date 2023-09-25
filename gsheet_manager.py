import gspread
import gspread_dataframe
import pandas as pd
import numpy as np
from datetime import date
import json

class gspreadsheet_manager:
    def __init__(self, gsheet=None):
        self.json_file_path = None
        self.spreadsheet_url = None
        self.gc = None
        self.doc = None
        self.worksheets = {}
        self.sheets_count = 0
    def set_json_path_and_url(self, json_file_path, gsheet_url):
        self.json_file_path = json_file_path
        self.spreadsheet_url = gsheet_url
    def open_spreadsheet(self):
        if (not self.json_file_path) or (not self.spreadsheet_url):
            return False
        try:
            self.gc = gspread.service_account(self.json_file_path)
            self.doc = self.gc.open_by_url(self.spreadsheet_url)
            return self.doc
        except Exception as e:
            print(f"Error occured opening sheet. {self.json_file_path} and {self.spreadsheet_url}")
            print(e)
            return False
    def open_worksheet(self, sheet_name):
        self.worksheets[sheet_name] = self.doc.worksheet(sheet_name)
        self.sheets_count += 1
        return self.worksheets[sheet_name]
    def update(self, which, where=None, what=None):
        if which in self.worksheets.keys():
            if not where:
                self.worksheets[which].update(where, self.convert_dates_to_strings(what))
                return True
            else:
                self.worksheets[which].update(self.convert_dates_to_strings(what))
                return True
        else:
            print(f"No such sheet:{which}")
            return False
    def update_sheet_with_df(self, which, what):
        return self.update(which, where=None, what=what)
    def convert_dates_to_strings(self, df):
        df_copy = df.copy()  # Create a copy of the DataFrame to avoid modifying the original
        date_columns = [cn for cn in df_copy.columns.tolist() if 'date' in cn]
        print(f"columns including date data: {date_columns}")
        for col in date_columns:
            df_copy[col] = df_copy[col].astype(str)
            # df_copy[col] = df_copy[col].dt.strftime('%Y-%m-%d')
        return df_copy
class sheet_manager_for_ffbe():
    def __init__(self):
        self.sheets = {}
        self.gm = gspreadsheet_manager()
        self.json_path = r"D:\Python\board-for-ffbe-973785f1358b.json"
        self.sheet_url = "https://docs.google.com/spreadsheets/d/1rSAyiMHyqeD-odGbJxF4TUlUZEMQp_so0Z6_2D6L6Hk/edit?pli=1#gid=1590214290"
        self.gm.set_json_path_and_url(self.json_path, self.sheet_url)
        print(self.gm.open_spreadsheet())
        # sheet_name = 'test'
        # sheet_test = gm.open_worksheet(sheet_name)
        # data = pd.DataFrame(np.random.randint(0, 100, size=(5, 10)))
        # sheet_test.update(data.values.tolist())
    def open_sheets(self):
        sheets_to_open = [
            'log', 'board', 'defenders', 'attackers', 'defender_board', 'attacker_board', 'score', 'test'
        ]
        for s in sheets_to_open:
            self.sheets[s] = self.gm.open_worksheet(s)
    def update_sheet_with_df(self, sheet_name, df):
        df_str = self.gm.convert_dates_to_strings(df)
        return self.sheets[sheet_name].update([df_str.columns.tolist()] + df_str.values.tolist())
    def update_sheet_with_df_including_index(self, sheet_name, df):
        gspread_dataframe.set_with_dataframe(self.sheets[sheet_name], df)
        # df_str = self.gm.convert_dates_to_strings(df)
        # print(df_str.dtypes)
        # if len(df_str):
        #     df_to_write = df_str.fillna('')
        #     return self.sheets[sheet_name].update([[''] + df_to_write.columns.tolist()] + df_to_write.reset_index().values.tolist())
        # else:
        #     return False
if __name__ == '__main__':
    gm = sheet_manager_for_ffbe()
    gm.open_sheets()
    data = pd.DataFrame(np.random.randint(0,100,size=(3,5)))
    gm.update_sheet_with_df('test', data)
    gm.update_sheet_with_df_including_index('attackers', data)

    # json_path = r"D:\Python\board-for-ffbe-973785f1358b.json"
    # sheet_url = "https://docs.google.com/spreadsheets/d/1rSAyiMHyqeD-odGbJxF4TUlUZEMQp_so0Z6_2D6L6Hk/edit?pli=1#gid=1590214290"
    # gm.set_json_path_and_url(json_path, sheet_url)
    # print(gm.open_spreadsheet())
    # sheet_name = 'test'
    # sheet_test = gm.open_worksheet(sheet_name)
    # data = pd.DataFrame(np.random.randint(0,100,size=(5,10)))
    # sheet_test.update(data.values.tolist())
    # sheet_test.update('test_range', data.values.tolist())