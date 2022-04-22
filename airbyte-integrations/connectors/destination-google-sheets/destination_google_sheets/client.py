#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Dict

import pygsheets
from google.auth.transport.requests import Request
from google.oauth2 import credentials as client_account
from pygsheets.client import Client as pygsheets_client

# the list of required scopes/permissions
# more info: https://developers.google.com/sheets/api/guides/authorizing#OAuth2Authorizing
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]


class GoogleSheetsClient:
    def __init__(self, config: Dict):
        self.config = config
        self.retries = 100  # max number of backoff retries

    def authorize(self) -> pygsheets_client:
        input_creds = self.config.get("credentials")
        auth_creds = client_account.Credentials.from_authorized_user_info(info=input_creds)
        client = pygsheets.authorize(custom_credentials=auth_creds, scopes=SCOPES)

        # obtain new access_token using refresh_token
        client.oauth.refresh(Request())

        # Increase max number of retries if Rate Limit is reached. Error: <HttpError 429>
        client.drive.retries = self.retries  # for google drive api
        client.sheet.retries = self.retries  # for google sheets api

        return client
