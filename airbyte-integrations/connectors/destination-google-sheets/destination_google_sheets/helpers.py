#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import re
from typing import List

from pygsheets import Spreadsheet, Worksheet, client
from pygsheets.exceptions import WorksheetNotFound


def get_spreadsheet_id(id_or_url: str) -> str:
    if re.match(r"(http://)|(https://)", id_or_url):
        m = re.search(r"(/)([-\w]{40,})([/]?)", id_or_url)
        if m.group(2):
            return m.group(2)
    else:
        return id_or_url


def connection_test_write(client: client) -> bool:
    wks_name: str = "_airbyte_conn_test"
    test_data: List[str] = ["conn_test", "success"]

    def add_test_wks(client: Spreadsheet, name: str = wks_name) -> Worksheet:
        client.add_worksheet(name, rows=2, cols=1)
        return client.worksheet_by_title(name)

    def populate_test_wks(wks: Worksheet) -> Worksheet:
        wks.append_table(test_data, dimension="COLUMNS")
        return wks

    def check_values(wks: Worksheet) -> bool:
        value = wks.get_value("A2")
        return True if value == test_data[1] else False

    def remove_test_wks(client: Spreadsheet, name: str = wks_name):
        wks = client.worksheet_by_title(name)
        client.del_worksheet(wks)

    try:
        if client.worksheets("title", wks_name):
            remove_test_wks(client)
        result: bool = check_values(populate_test_wks(add_test_wks(client)))
    except WorksheetNotFound:
        result: bool = check_values(populate_test_wks(add_test_wks(client)))
    finally:
        remove_test_wks(client)

    return result
