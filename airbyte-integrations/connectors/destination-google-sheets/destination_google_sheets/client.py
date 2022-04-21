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
        # max number of backoff retries
        self.retries = 20

    def authorize(self) -> pygsheet_client:
        input_creds = GoogleSheetsAuth.get_credentials(self.config)
        authenticated_creds = GoogleSheetsAuth.get_authenticated_google_credentials(input_creds)
        client = pygsheets.authorize(custom_credentials=authenticated_creds, scopes=SCOPES)

        # Increase max number of retries if Rate Limit is reached. Error: <HttpError 429>
        client.drive.retries = self.retries
        client.sheet.retries = self.retries

        return client
