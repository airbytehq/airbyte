#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import requests
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from requests.auth import AuthBase

DEFAULT_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]


class ServiceAccountAuthenticator(AuthBase):
    def __init__(self, service_account_info: str, email: str, scopes=None):
        self.scopes = scopes or DEFAULT_SCOPES
        self.credentials: Credentials = Credentials.from_service_account_info(service_account_info, scopes=self.scopes).with_subject(email)

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        if not self.credentials.valid:
            # We pass a dummy request because the refresh iface requires it
            self.credentials.refresh(Request())
        self.credentials.apply(request.headers)
        return request
