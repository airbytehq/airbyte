#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import re
import pandas as pd
from pygsheets import client, Spreadsheet, Worksheet
from pygsheets.exceptions import WorksheetNotFound
from requests import codes as status_codes
    
def error_handler(error) -> bool:
    return error.resp.status != status_codes.TOO_MANY_REQUESTS

def get_spreadsheet_id(id_or_url: str) -> str:
    if re.match(r"(http://)|(https://)", id_or_url):
        m = re.search(r"(/)([-\w]{40,})([/]?)", id_or_url)
        if m.group(2):
            return m.group(2)
    else:
        return id_or_url
    
def create_test_df() -> pd.DataFrame:
    data = pd.DataFrame()
    data['conn_test'] = ["success"]
    return data

def connection_test_write(client: client, config: str) -> bool:
    wks_name = "_airbyte_conn_test"
    test_range = (0,0)
    
    sh = client.open_by_key(get_spreadsheet_id(config["spreadsheet_id"]))
    
    def add_test_wks(sh: Spreadsheet, name: str = wks_name) -> Spreadsheet:
        sh.add_worksheet(name, rows=2, cols=1)
        return sh.worksheet_by_title(name)
    
    def populate_test_wks(wks: Worksheet) -> Worksheet:
        wks.set_dataframe(create_test_df(), test_range)
        return wks
    
    def check_values(wks: Worksheet) -> bool:
        value = wks.get_value('A2')
        return True if value == "success" else False
    
    def remove_test_wks(sh: Spreadsheet, name: str = wks_name) -> None:
        wks = sh.worksheet_by_title(name)
        sh.del_worksheet(wks)
        
    try:
        if sh.worksheets('title', wks_name):
            remove_test_wks(sh)
        result = check_values(populate_test_wks(add_test_wks(sh)))
    except WorksheetNotFound:
        result = check_values(populate_test_wks(add_test_wks(sh)))
    finally:
        remove_test_wks(sh)

    return result
    