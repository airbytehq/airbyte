#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import re
from typing import List

from pygsheets import Spreadsheet, Worksheet
from pygsheets.exceptions import WorksheetNotFound


def get_spreadsheet_id(id_or_url: str) -> str:
    if re.match(r"(http://)|(https://)", id_or_url):
        m = re.search(r"(/)([-\w]{40,})([/]?)", id_or_url)
        if m.group(2):
            return m.group(2)
    else:
        return id_or_url


def connection_test_write(spreadsheet: Spreadsheet) -> bool:
    wks_name: str = "_airbyte_conn_test"
    test_data: List[str] = ["conn_test", "success"]

    # access underlying pygsheets methods for test purposes
    spreadsheet = spreadsheet.spreadsheet

    def add_test_wks(spreadsheet: Spreadsheet, name: str = wks_name) -> Worksheet:
        spreadsheet.add_worksheet(name, rows=2, cols=1)
        return spreadsheet.worksheet_by_title(name)

    def populate_test_wks(wks: Worksheet) -> Worksheet:
        wks.append_table(test_data, dimension="COLUMNS")
        return wks

    def check_values(wks: Worksheet) -> bool:
        value = wks.get_value("A2")
        return True if value == test_data[1] else False

    def remove_test_wks(spreadsheet: Spreadsheet, name: str = wks_name):
        wks = spreadsheet.worksheet_by_title(name)
        spreadsheet.del_worksheet(wks)

    try:
        if spreadsheet.worksheets("title", wks_name):
            remove_test_wks(spreadsheet)
        result: bool = check_values(populate_test_wks(add_test_wks(spreadsheet)))
    except WorksheetNotFound:
        result: bool = check_values(populate_test_wks(add_test_wks(spreadsheet)))
    finally:
        remove_test_wks(spreadsheet)

    return result
