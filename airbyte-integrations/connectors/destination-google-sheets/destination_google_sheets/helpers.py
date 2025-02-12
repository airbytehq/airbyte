#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import re
from typing import List

from pygsheets import Spreadsheet, Worksheet
from pygsheets.exceptions import WorksheetNotFound

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import ConfiguredAirbyteCatalog


STREAMS_COUNT_LIMIT = 200


logger = AirbyteLogger()


def get_spreadsheet_id(id_or_url: str) -> str:
    if re.match(r"(https://)", id_or_url):
        m = re.search(r"(/)([-\w]{40,})([/]?)", id_or_url)
        if m.group(2):
            return m.group(2)
        else:
            logger.error(
                "The provided URL doesn't match the requirements. See <a href='https://docs.airbyte.com/integrations/destinations/google-sheets#sheetlink'>this guide</a> for more details."
            )
    else:
        return id_or_url


def get_streams_from_catalog(catalog: ConfiguredAirbyteCatalog, limit: int = STREAMS_COUNT_LIMIT):
    streams_count = len(catalog.streams)
    if streams_count > limit:
        logger.warn(f"Only {limit} of {streams_count} will be processed due to Google Sheets (worksheet count < {limit}) limitations.")
        return catalog.streams[:limit]
    return catalog.streams


class ConnectionTest:
    """
    Performs connection test write operation to ensure the target spreadsheet is available for writing.
    Initiating the class itself, performs the connection test and stores the result in ConnectionTest.result property.
    """

    def __init__(self, spreadsheet: Spreadsheet):
        self.spreadsheet = spreadsheet
        self.wks_name: str = "_airbyte_conn_test"
        self.test_data: List[str] = ["conn_test", "success"]

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

        self.remove_test_wks()
        return result
