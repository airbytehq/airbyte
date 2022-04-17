#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Dict, List

import pygsheets
from pygsheets import client
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

    def list_worksheets(self) -> List:
        """
        Returns the existing worksheets inside of target spreadsheet.
        """
        wks_list = []
        for wks in self.client.worksheets():
            wks_list.append(wks.title)
        yield from wks_list

    def clean_worksheet(self, name: str):
        """
        Cleans up the existing records inside the worksheet or creates one, if doesn't exist.
        """
        try:
            wks = self.open_worksheet(name)
            wks.clear()
        except WorksheetNotFound:
            self.client.add_worksheet(name)

    def open_worksheet(self, name: str):
        try:
            wks = self.client.worksheet_by_title(name)
        except WorksheetNotFound:
            wks = self.client.add_worksheet(name)
        finally:
            return wks
