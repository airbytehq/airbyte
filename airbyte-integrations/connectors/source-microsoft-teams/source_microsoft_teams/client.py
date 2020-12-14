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
import json
import pkgutil

import msal
import requests

from typing import Dict, Tuple
from msal.exceptions import MsalServiceError

from airbyte_protocol import AirbyteStream


class Client:
    MICROSOFT_GRAPH_BASE_API_URL = "https://graph.microsoft.com/"
    MICROSOFT_GRAPH_API_VERSION = "v1.0"

    def __init__(self, config: Dict):
        self.ENTITY_MAP = {
            "users": self.users,
        }
        self.configs = config

    def _get_api_url(self, endpoint: str) -> str:
        api_url = f'{self.MICROSOFT_GRAPH_BASE_API_URL}{self.MICROSOFT_GRAPH_API_VERSION}/{endpoint}/'
        return api_url

    def _get_access_token(self) -> Dict[str, str]:
        scope = ['https://graph.microsoft.com/.default']
        app = msal.ConfidentialClientApplication(self.configs['client_id'],
                                                 authority=f"https://login.microsoftonline.com/"
                                                           f"{self.configs['tenant_id']}",
                                                 client_credential=self.configs['client_secret'])
        result = app.acquire_token_silent(scope, account=None)
        if not result:
            result = app.acquire_token_for_client(scopes=scope)
        if 'access_token' in result:
            return result['access_token']
        else:
            raise MsalServiceError(error=result.get('error'), error_description=result.get("error_description"))

    def _make_request(self, endpoint: str) -> Dict:
        api_url = self._get_api_url(endpoint)
        access_token = self._get_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        response = requests.get(api_url, headers=headers)
        return response.json()['value']

    def health_check(self) -> Tuple[bool, object]:
        try:
            self._get_access_token()
            return True, None
        except MsalServiceError as err:
            return False, err.args[0]

    def get_streams(self):
        streams = []
        for schema, method in self.ENTITY_MAP.items():
            raw_schema = json.loads(pkgutil.get_data(self.__class__.__module__.split('.')[0], f'schemas/{schema}.json'))
            streams.append(AirbyteStream(name=schema, json_schema=raw_schema))
        return streams

    def users(self):
        users = self._make_request('users')
        return users
