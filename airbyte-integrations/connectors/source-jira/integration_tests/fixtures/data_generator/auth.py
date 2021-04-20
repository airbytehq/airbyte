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
import pathlib

from requests.auth import HTTPBasicAuth


class AuthClient:
    base_config_path = "secrets/config.json"
    base_headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def __init__(self):
        self.configs = None
        super(AuthClient, self).__init__()

    def _get_configs(self):
        if not self.configs:
            source_directory = pathlib.Path(__file__).resolve().parent.parent.parent.parent
            configs_path = source_directory.joinpath(self.base_config_path)
            with open(configs_path) as json_configs:
                self.configs = json.load(json_configs)
        return self.configs

    def get_auth(self):
        configs = self._get_configs()
        auth = HTTPBasicAuth(configs.get("email"), configs.get("api_token"))
        return auth

    def get_headers(self):
        headers = self.base_headers
        return headers

    def get_base_url(self):
        configs = self._get_configs()
        base_url = f'https://{configs.get("domain")}/rest/api/3/'
        return base_url
