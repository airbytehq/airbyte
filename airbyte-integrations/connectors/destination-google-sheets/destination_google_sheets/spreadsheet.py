#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import List, Mapping

from pygsheets import Spreadsheet, Worksheet
from pygsheets.client import Client as pygsheets_client
from pygsheets.exceptions import WorksheetNotFound


class GoogleSheets:
    def __init__(self, client: pygsheets_client, spreadsheet_id: str):
        self.client = client
        self.spreadsheet_id = spreadsheet_id

    @property
    def spreadsheet(self) -> Spreadsheet:
        """
        Returns pygsheets.Spreadsheet with opened target spreadsheet by key.
        """
        return self.client.open_by_key(self.spreadsheet_id)

    def open_worksheet(self, stream_name: str) -> Worksheet:
        """
        Opens the connection to target worksheet, if exists. Otherwise, creates one.
        """
        try:
            stream = self.spreadsheet.worksheet_by_title(stream_name)
        except WorksheetNotFound:
            stream = self.spreadsheet.add_worksheet(stream_name)
        return stream

    def clean_worksheet(self, stream_name: str):
        """
        Cleans up the existing records inside the worksheet or creates one, if doesn't exist.
        """
        try:
            stream = self.open_worksheet(stream_name)
            stream.clear()
        except WorksheetNotFound:
            self.spreadsheet.add_worksheet(stream_name)

    def set_headers(self, stream_name: str, headers_list: List[str]):
        """
        Sets headers belonging to the input stream
        """
        stream: Worksheet = self.open_worksheet(stream_name)
        if headers_list:
            stream.update_row(1, headers_list)

    def index_cols(self, stream: Worksheet) -> Mapping[str, int]:
        """
        Helps to find the index of every colums exists in worksheet.
        Returns: Mapping with column name and it's index.
            {"id": 1, "name": 2, ..., "other": 99}
        """
        header = stream[1]  # get the first row
        col_index = {}
        for i, col in enumerate(header):
            col_index[col] = i + 1
        return col_index

    def find_duplicates(self, stream: Worksheet, primary_key: str):
        """
        Finds the duplicated records inside of target worksheet.
        Returns: List of indexes of rows to remove from target worksheet.
            [1, 4, 5, ..., 99]
        """
        rows_unique_values, rows_to_delete = {}, []
        pk_col_index = self.index_cols(stream)[primary_key]

        # get all values except 0, because it's a header value
        pk_col_values = stream.get_col(pk_col_index, include_tailing_empty=False)[1:]

        for i, row_value in enumerate(pk_col_values, 2):
            if row_value not in rows_unique_values:
                rows_unique_values[row_value] = None
            else:
                rows_to_delete.append(i)

        # reverse the order of the list
        rows_to_delete.reverse()

        return rows_to_delete

    def remove_duplicates(self, stream: Worksheet, rows_list: list):
        """
        Removes duplicated rows, provided by `rows_list` as list of indexes.

        We are working with delete operation in offline mode, to decrease the number of API calls.
        1) Unlink the spreadsheet (make it for offline use)
        2) Perform delete operation and update the actual row index
        3) Link the spreadsheet (sync with online version) using batch_update method.
        """
        stream.unlink()
        [stream.delete_rows(row, 1) for row in rows_list]
        stream.link()
