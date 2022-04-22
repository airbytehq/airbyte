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


class ConnectionTest:

    """
    Performs connection test write operation to ensure the target spreadsheet is available for writing.
    Initiating the class itself, performs the connection test and stores the result in ConnectionTest.result property.
    """

    def __init__(self, spreadsheet: Spreadsheet):
        self.spreadsheet = spreadsheet
        self.wks_name: str = "_airbyte_conn_test"
        self.test_data: List[str] = ["conn_test", "success"]
        self.result = self.perform_connection_test()

    def add_test_wks(self) -> Worksheet:
        self.spreadsheet.spreadsheet.add_worksheet(self.wks_name, rows=2, cols=1)
        return self.spreadsheet.open_worksheet(self.wks_name)

    def remove_test_wks(self):
        wks = self.spreadsheet.open_worksheet(self.wks_name)
        self.spreadsheet.spreadsheet.del_worksheet(wks)

    def populate_test_wks(self, wks: Worksheet) -> Worksheet:
        wks.append_table(self.test_data, dimension="COLUMNS")
        return wks

    def check_values(self, wks: Worksheet) -> bool:
        value = wks.get_value("A2")
        return True if value == self.test_data[1] else False

    def perform_connection_test(self) -> bool:
        try:
            if self.spreadsheet.spreadsheet.worksheets("title", self.wks_name):
                self.remove_test_wks()
            result: bool = self.check_values(self.populate_test_wks(self.add_test_wks()))
        except WorksheetNotFound:
            result: bool = self.check_values(self.populate_test_wks(self.add_test_wks()))
        finally:
            self.remove_test_wks()
        return result
