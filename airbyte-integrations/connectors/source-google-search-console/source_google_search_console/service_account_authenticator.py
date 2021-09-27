#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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
