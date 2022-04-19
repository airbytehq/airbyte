#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Dict, List, Mapping

import pygsheets
from pygsheets import Worksheet, client
from pygsheets.exceptions import WorksheetNotFound

from .auth import SCOPES, GoogleSpreadsheetsAuth
from .helpers import get_spreadsheet_id


class GoogleSpreadsheetsClient:
    def __init__(self, config: Dict):
        self.config = config

    @property
    def client(self) -> client:
        """
        Returns pygsheets.client with opened target spreadsheet.
        """
        config_creds = GoogleSpreadsheetsAuth.get_credentials(self.config)
        authenticated_creds = GoogleSpreadsheetsAuth.get_authenticated_google_credentials(config_creds)
        client = pygsheets.authorize(custom_credentials=authenticated_creds, scopes=SCOPES)
        
        return client.open_by_key(self.spreadsheet_id)

    @property
    def spreadsheet_id(self) -> str:
        """
        Returns the id from the input url provided, or the actual id, if provided by user.
        """
        return get_spreadsheet_id(self.config["spreadsheet_id"])

    def clean_worksheet(self, stream_name: str):
        """
        Cleans up the existing records inside the worksheet or creates one, if doesn't exist.
        """
        try:
            stream = self.open_worksheet(stream_name)
            stream.clear()
        except WorksheetNotFound:
            self.client.add_worksheet(stream_name)

    def open_worksheet(self, stream_name: str) -> Worksheet:
        """
        Opens the connection to target worksheet, if exists. Otherwise, creates one.
        """
        try:
            stream = self.client.worksheet_by_title(stream_name)
        except WorksheetNotFound:
            stream = self.client.add_worksheet(stream_name)
        finally:
            return stream
        
    def set_headers(self, stream_name: str, headers_list: List[str]):
        """
        Sets headers belonging to the input stream
        """
        stream: Worksheet = self.open_worksheet(f"{stream_name}")
        stream.update_row(1, headers_list)

    def index_cols(self, stream: Worksheet) -> Mapping[str, int]:
        """
        Helps to find the index of every colums exists in worksheet.
        Returns: Mapping with column name and it's index.
            {"id": 1, "name": 2, ..., "other": 99}
        """
        header = stream[1]
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
        rows_unique, rows_to_delete = [], []
        
        pk_col_index = self.index_cols(stream)[primary_key]
        col_values = stream.get_col(pk_col_index, include_tailing_empty=False)[1:] # get everything but 0 position.
        
        for i, row in enumerate(col_values, 1):
            if col_values[i - 1] not in rows_unique:
                rows_unique.append(row)
            else:
                rows_to_delete.append(i + 1)
                
        rows_to_delete.reverse() # reverse the order of the list
        return rows_to_delete

    def remove_duplicates(self, stream: Worksheet, rows_list: list):
        """
        Removes duplicated rows, provided by `rows_list` as list of indexes.
        """
        stream.unlink()
        [stream.delete_rows(row, 1) for row in rows_list]
        stream.sync()
        