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

from base_python import AirbyteLogger
from base_singer import BaseSingerSource
from tap_intercom.client import IntercomClient, IntercomError


class SourceIntercomSinger(BaseSingerSource):
    tap_cmd = "tap-intercom"
    tap_name = "Intercom API"
    api_error = IntercomError

    def transform_config(self, raw_config) -> Mapping[str, Any]:
        return {
            "user_agent": "airbyte",
            "access_token": raw_config["access_token"],
            "start_date": raw_config["start_date"],
        }

    def try_connect(self, logger: AirbyteLogger, config: dict):
        client = IntercomClient(user_agent=config["user_agent"], access_token=config["access_token"])
        ok = client.check_access_token()
        if not ok:
            raise IntercomError("No data. Please check your permissions.")
