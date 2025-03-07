#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import requests
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from requests.auth import AuthBase

from source_google_search_console.exceptions import UnauthorizedServiceAccountError


DEFAULT_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]


class ServiceAccountAuthenticator(AuthBase):
    def __init__(self, service_account_info: str, email: str, scopes=None):
        self.scopes = scopes or DEFAULT_SCOPES
        self.service_account_info = service_account_info
        self.email = email

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        try:
            credentials: Credentials = Credentials.from_service_account_info(self.service_account_info, scopes=self.scopes).with_subject(
                self.email
            )
            if not credentials.valid:
                # We pass a dummy request because the refresh iface requires it
                credentials.refresh(Request())
            credentials.apply(request.headers)
            return request
        except Exception:
            raise UnauthorizedServiceAccountError
