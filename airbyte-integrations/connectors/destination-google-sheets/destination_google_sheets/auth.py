#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

# import json
from typing import Dict, List

from google.oauth2 import credentials as client_account

# from google.oauth2 import service_account

# the list of required scopes/permissions
# more info: https://developers.google.com/sheets/api/guides/authorizing#OAuth2Authorizing
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]


class GoogleSpreadsheetsAuth:
    @staticmethod
    def get_authenticated_google_credentials(credentials: Dict[str, str], scopes: List[str] = SCOPES) -> client_account.Credentials:
        if credentials.get("auth_type") == "Client":
            return client_account.Credentials.from_authorized_user_info(info=credentials)
        if credentials.get("auth_type") == "Service":
            # TODO: make it work with service account
            # return service_account.Credentials.from_service_account_info(json.loads(credentials["service_account_info"]), scopes=scopes)
            raise NotImplementedError("This Authentication method has is not implemented yet, please use OAuth2.0.")

    @staticmethod
    def get_credentials(config) -> Dict:
        """
        Returns:
            :: credentials property from user's config input.
        """
        # TODO: make it work with service account
        # if config.get("credentials_json"):
        #     credentials = {"auth_type": "Service", "service_account_info": config.get("credentials_json")}
        #     return credentials
        return config.get("credentials")
