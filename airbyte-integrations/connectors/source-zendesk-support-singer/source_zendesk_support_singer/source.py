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

from airbyte_protocol import AirbyteConnectionStatus, Status
from base_python import AirbyteLogger
from base_singer import SingerSource

TAP_CMD = "tap-zendesk"


class SourceZendeskSupportSinger(SingerSource):
    def check_config(self, logger: AirbyteLogger, config_path: str, config: json) -> AirbyteConnectionStatus:
        try:
            self.discover(logger, config_path)
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception:
            logger.error("Exception while connecting to the Zendesk Support API")
            return AirbyteConnectionStatus(
                status=Status.FAILED,
                message="Unable to connect to the Zendesk Support API with the provided credentials.  Please make sure the "
                "input credentials and environment are correct. ",
            )

    def discover_cmd(self, logger: AirbyteLogger, config_path: str) -> str:
        return f"{TAP_CMD} -c {config_path} --discover"

    def read_cmd(self, logger: AirbyteLogger, config_path: str, catalog_path: str, state_path: str = None) -> str:
        state_opt = f"--state {state_path}" if state_path else ""
        return f"{TAP_CMD} --config {config_path} --catalog {catalog_path} {state_opt}"
