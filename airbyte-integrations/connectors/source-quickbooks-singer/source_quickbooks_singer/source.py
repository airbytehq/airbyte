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


import json

from base_python import AirbyteLogger
from base_singer import BaseSingerSource
from requests_oauthlib import OAuth2Session
from tap_quickbooks.client import (
    PROD_ENDPOINT_BASE,
    SANDBOX_ENDPOINT_BASE,
    TOKEN_REFRESH_URL,
    Quickbooks4XXException,
    Quickbooks5XXException,
    QuickbooksAuthenticationError,
)


class SourceQuickbooksSinger(BaseSingerSource):
    tap_cmd = "tap-quickbooks"
    tap_name = "Quickbooks API"
    api_error = Exception

    def _write_config(self, token):
        logger = AirbyteLogger()
        logger.info("Credentials Refreshed")

    def try_connect(self, logger: AirbyteLogger, config: json):
        token = {"refresh_token": config["refresh_token"], "token_type": "Bearer", "access_token": "wrong", "expires_in": "-30"}
        extra = {"client_id": config["client_id"], "client_secret": config["client_secret"]}

        sandbox = bool(config.get("sandbox", False))

        user_agent = config["user_agent"]
        realm_id = config["realm_id"]
        session = OAuth2Session(
            config["client_id"],
            token=token,
            auto_refresh_url=TOKEN_REFRESH_URL,
            auto_refresh_kwargs=extra,
            token_updater=self._write_config,
        )

        endpoint = f"/v3/company/{realm_id}/query"
        params = {"query": "SELECT * FROM CompanyInfo"}
        headers = {"Accept": "application/json", "User-Agent": user_agent}

        if sandbox:
            full_url = SANDBOX_ENDPOINT_BASE + endpoint
        else:
            full_url = PROD_ENDPOINT_BASE + endpoint

        response = session.request("GET", full_url, headers=headers, params=params)

        if response.status_code >= 500:
            raise Quickbooks5XXException(response.text)
        elif response.status_code in (401, 403):
            raise QuickbooksAuthenticationError(response.text)
        elif response.status_code >= 400:
            raise Quickbooks4XXException(response.text)
