#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
from typing import Dict

import pygsheets
from google.auth.transport.requests import Request
from google.oauth2 import credentials as client_account
from google.oauth2 import service_account
from pygsheets.client import Client as pygsheets_client

from airbyte_cdk import AirbyteLogger


# the list of required scopes/permissions
# more info: https://developers.google.com/sheets/api/guides/authorizing#OAuth2Authorizing
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]


class GoogleSheetsClient:
    logger = AirbyteLogger()

    def __init__(self, config: Dict):
        self.config = config
        self.retries = 100  # max number of backoff retries

    def authorize(self) -> pygsheets_client:
        credentials = self.config.get("credentials", {})
        auth_type = credentials.get("auth_type")

        if auth_type == "service":
            service_account_info = credentials.get("service_account_info")
            if isinstance(service_account_info, str):
                service_account_info = json.loads(service_account_info)
            auth_creds = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
        else:
            input_creds = self.config.get("credentials")
            auth_creds = client_account.Credentials.from_authorized_user_info(info=input_creds)
        try:
            client = pygsheets.authorize(custom_credentials=auth_creds)
        except Exception as e:
            self.logger.error(f"Failed to authorize with service account. Error: {str(e)}")
            self.logger.error(f"Error type: {type(e)}")
            raise

        # Increase max number of retries if Rate Limit is reached. Error: <HttpError 429>
        client.drive.retries = self.retries  # for google drive api
        client.sheet.retries = self.retries  # for google sheets api

        # Only check token expiration for OAuth authentication
        if auth_type != "service":
            if client.oauth.expired:
                self.logger.info("Auth session is expired. Refreshing...")
                client.oauth.refresh(Request())
                if not client.oauth.expired:
                    self.logger.info("Successfully refreshed auth session")
                else:
                    self.logger.fatal("The token is expired and could not be refreshed, please check the credentials are still valid!")

        return client
