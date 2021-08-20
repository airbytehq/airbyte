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


from typing import Any, Mapping, Optional, Tuple

from base_python import BaseClient

from .api import API, AdminAPI, DriveAPI, IncrementalStreamAPI, LoginsAPI, MobileAPI, OAuthTokensAPI


class Client(BaseClient):
    def __init__(self, credentials_json: str, email: str, lookback: Optional[int] = None):
        self._api = API(credentials_json, email, lookback)
        self._apis = {
            "admin": AdminAPI(self._api),
            "drive": DriveAPI(self._api),
            "logins": LoginsAPI(self._api),
            "mobile": MobileAPI(self._api),
            "oauth_tokens": OAuthTokensAPI(self._api),
        }
        super().__init__()

    def stream_has_state(self, name: str) -> bool:
        """Tell if stream supports incremental sync"""
        return isinstance(self._apis[name], IncrementalStreamAPI)

    def get_stream_state(self, name: str) -> Any:
        """Get state of stream with corresponding name"""
        return self._apis[name].state

    def set_stream_state(self, name: str, state: Any):
        """Set state of stream with corresponding name"""
        self._apis[name].state = state

    def _enumerate_methods(self) -> Mapping[str, callable]:
        return {name: api.list for name, api in self._apis.items()}

    def health_check(self) -> Tuple[bool, str]:
        alive = True
        error_msg = None

        try:
            params = {"userKey": "all", "applicationName": "login"}
            self._api.get(name="activities", params=params)
        except Exception as error:
            alive = False
            error_msg = repr(error)

        return alive, error_msg
