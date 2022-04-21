#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Dict

import pygsheets
from pygsheets import client as pygsheet_client

from .auth import SCOPES, GoogleSheetsAuth


class GoogleSheetsClient:
    def __init__(self, config: Dict):
        self.config = config

    def authorize(self) -> pygsheet_client:
        input_creds = GoogleSheetsAuth.get_credentials(self.config)
        authenticated_creds = GoogleSheetsAuth.get_authenticated_google_credentials(input_creds)
        return pygsheets.authorize(custom_credentials=authenticated_creds, scopes=SCOPES)
