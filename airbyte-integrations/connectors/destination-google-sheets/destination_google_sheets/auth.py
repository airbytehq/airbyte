#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pygsheets
# import json
from typing import Dict, List
from google.oauth2 import credentials as client_account
# from google.oauth2 import service_account

# the list of required scopes/permissions, more info: https://developers.google.com/sheets/api/guides/authorizing#OAuth2Authorizing
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets", # read/write access for sheets
    "https://www.googleapis.com/auth/drive.file" # read/write access to files created or opened by the airbyte connector
]

class GoogleSpreadsheetsAuth:

    @staticmethod
    def get_authenticated_google_credentials(credentials: Dict[str, str], scopes: List[str] = SCOPES):
        if credentials.get("auth_type") == "Client":
            return client_account.Credentials.from_authorized_user_info(info=credentials)
        if credentials.get("auth_type") == "Service":
            # TODO: make it work with service account
            # return service_account.Credentials.from_service_account_info(json.loads(credentials["service_account_info"]), scopes=scopes)
            raise NotImplementedError("This Authentication method has is not implemented yet, please use OAuth2.0.")
    
    @classmethod
    def authenticate(self, config: Dict):
        config_creds = self.get_credentials(config)
        auth_google_creds = self.get_authenticated_google_credentials(config_creds)
        return pygsheets.authorize(custom_credentials=auth_google_creds, scopes=SCOPES)
    
    @staticmethod
    def get_credentials(config):
        """
        Returns:
            :: credentials property from user's config input.
        """
        # TODO: make it work with service account
        # if config.get("credentials_json"):
        #     credentials = {"auth_type": "Service", "service_account_info": config.get("credentials_json")}
        #     return credentials
        return config.get("credentials")

    
        
