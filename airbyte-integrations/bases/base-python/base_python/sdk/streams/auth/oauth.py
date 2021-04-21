"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Any, Mapping

import requests
from base_python.sdk.streams.auth.core import HttpAuthenticator


class Oauth2Authenticator(HttpAuthenticator):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        access_token: str = None,
    ):
        # set expires at timestamp to something in the past.
        raise NotImplementedError

    def get_auth_header(self) -> Mapping[str, Any]:

        # TODO
        raise NotImplementedError

    def get_access_token(self):
        if self.token_has_expired():
            self.refresh_access_token()

    def token_has_expired(self, response: requests.Response = None) -> bool:
        # time-based? Does it require a request?
        raise NotImplementedError

    def refresh_access_token(self) -> None:
        # how do we know where to refresh the access token?
        raise NotImplementedError
