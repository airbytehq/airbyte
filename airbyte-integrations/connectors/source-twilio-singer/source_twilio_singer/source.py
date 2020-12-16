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
from base_singer import AirbyteLogger, SingerSource
from twilio.base.exceptions import TwilioException
from twilio.rest import Client

TAP_CMD = "tap-twilio"


class SourceTwilioSinger(SingerSource):
    def check_config(self, logger: AirbyteLogger, config_path: str, config: json) -> AirbyteConnectionStatus:
        try:
            client = Client(config["account_sid"], config["auth_token"])
            client.api.accounts.list()
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except TwilioException as error:
            logger.error(str(error))
            return AirbyteConnectionStatus(status=Status.FAILED, message=str(error))

    def discover_cmd(self, logger, config_path) -> str:
        return f"{TAP_CMD} --config {config_path} --discover"

    def read_cmd(self, logger, config_path, catalog_path, state_path=None) -> str:
        config_option = f"--config {config_path}"
        properties_option = f"--catalog {catalog_path}"
        state_opt = f"--state {state_path}" if state_path else ""
        return f"{TAP_CMD} {config_option} {properties_option} {state_opt}"
