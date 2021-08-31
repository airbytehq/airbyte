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

import pendulum
from airbyte_cdk.sources.streams.http.auth.oauth import Oauth2Authenticator
from oauth2client.service_account import ServiceAccountCredentials

DEFAULT_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]


class ServiceAccountAuthenticator(Oauth2Authenticator):
    def __init__(self, service_account_info, scopes=None):
        self.scopes = scopes or DEFAULT_SCOPES
        self.credentials = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, self.scopes)
        self._access_token = None
        self._access_token_object = None
        self._token_expiry_date = pendulum.now().subtract(days=1)

    def refresh_access_token(self):
        self._access_token_object = self.credentials.get_access_token()
        return self._access_token_object.access_token, self._access_token_object.expires_in
