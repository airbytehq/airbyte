#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import requests
from airbyte_cdk.sources.streams.http.rate_limiting import default_backoff_handler


class Pardot:
    def __init__(
        self,
        refresh_token: str = None,
        token: str = None,
        client_id: str = None,
        client_secret: str = None,
        is_sandbox: bool = None,
        start_date: str = None,
        api_type: str = None,
        pardot_business_unit_id: str = None,
    ):
        self.api_type = api_type.upper() if api_type else None
        self.refresh_token = refresh_token
        self.token = token
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.instance_url = None
        self.session = requests.Session()
        self.is_sandbox = is_sandbox is True or (isinstance(is_sandbox, str) and is_sandbox.lower() == "true")
        self.start_date = start_date
        self.pardot_business_unit_id = pardot_business_unit_id

    def login(self):
        login_url = f"https://{'test' if self.is_sandbox else 'login'}.salesforce.com/services/oauth2/token"
        login_body = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
        }

        resp = self._make_request("POST", login_url, body=login_body, headers={"Content-Type": "application/x-www-form-urlencoded"})

        auth = resp.json()
        self.access_token = auth["access_token"]
        self.instance_url = auth["instance_url"]

    @default_backoff_handler(max_tries=5, factor=15)
    def _make_request(
        self, http_method: str, url: str, headers: dict = None, body: dict = None, stream: bool = False, params: dict = None
    ) -> requests.models.Response:
        if http_method == "GET":
            resp = self.session.get(url, headers=headers, stream=stream, params=params)
        elif http_method == "POST":
            resp = self.session.post(url, headers=headers, data=body)
        resp.raise_for_status()

        return resp
