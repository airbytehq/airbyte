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

import requests
from base_python import AirbyteLogger
from base_singer import BaseSingerSource
from requests import HTTPError


class SourceGitlabSinger(BaseSingerSource):
    """
    Gitlab API Reference: https://docs.gitlab.com/ee/api/README.html
    """

    tap_cmd = "tap-gitlab"
    tap_name = "Gitlab API"
    api_error = HTTPError, Exception

    def transform_config(self, raw_config):
        return {**raw_config, "api_url": f'https://{raw_config["api_url"]}/'}

    def try_connect(self, logger: AirbyteLogger, config: dict):
        if not config["projects"] and not config["groups"]:
            raise Exception("Either groups or projects need to be provided for connect to Gitlab API")
        response = requests.get(f"{config['api_url']}api/v4/projects", params={"private_token": config["private_token"]})
        response.raise_for_status()
