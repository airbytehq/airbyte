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

import urllib.request

from airbyte_protocol import AirbyteConnectionStatus, Status
from base_singer import SingerSource


class SourceExchangeRatesApiSinger(SingerSource):
    def __init__(self):
        pass

    def check(self, logger, config_path) -> AirbyteConnectionStatus:
        try:
            code = urllib.request.urlopen("https://api.exchangeratesapi.io/").getcode()
            logger.info(f"Ping response code: {code}")
            return AirbyteConnectionStatus(status=Status.SUCCEEDED if (code==200) else Status.FAILED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"{str(e)}")

    def discover_cmd(self, logger, config_path) -> str:
        return "tap-exchangeratesapi | grep '\"type\": \"SCHEMA\"' | head -1 | jq -c '{\"streams\":[{\"stream\": .stream, \"schema\": .schema}]}'"

    def read_cmd(self, logger, config_path, catalog_path, state_path=None) -> str:
        state_option = f"--state {state_path}" if state_path else ""
        return f"tap-exchangeratesapi --config {config_path} {state_option}"

