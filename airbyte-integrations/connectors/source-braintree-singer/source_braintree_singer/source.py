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
import os
import tempfile
from datetime import datetime

import braintree
from airbyte_protocol import AirbyteConnectionStatus, Status
from base_python import AirbyteLogger, ConfigContainer
from base_singer import SingerSource
from braintree.exceptions.authentication_error import AuthenticationError
from dateutil import parser
from dateutil.relativedelta import relativedelta

TAP_CMD = "tap-braintree"

DISCOVER_CONFIG_FILE = os.path.join(tempfile.gettempdir(), "discover_configs.json")


class SourceBraintreeSinger(SingerSource):
    def transform_config(self, raw_config):
        # The tap-braintree singer moves the start_date 1 month earlier, this line fixes this.
        raw_config["start_date"] = (parser.parse(raw_config["start_date"]) + relativedelta(months=+1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        return raw_config

    def check(self, logger: AirbyteLogger, config_container: ConfigContainer) -> AirbyteConnectionStatus:
        try:
            json_config = config_container.rendered_config
            client = braintree.BraintreeGateway(
                braintree.Configuration(
                    environment=getattr(braintree.Environment, json_config["environment"]),
                    merchant_id=json_config["merchant_id"],
                    public_key=json_config["public_key"],
                    private_key=json_config["private_key"],
                )
            )
            client.transaction.search(
                braintree.TransactionSearch.created_at.between(datetime.now() + relativedelta(days=-1), datetime.now())
            )
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except AuthenticationError:
            logger.error("Exception while connecting to the Braintree API")
            return AirbyteConnectionStatus(
                status=Status.FAILED,
                message="Unable to connect to the Braintree API with the provided credentials. Please make sure the input credentials and environment are correct.",
            )

    def discover_cmd(self, logger: AirbyteLogger, config_path: str) -> str:
        with open(config_path) as config:
            config_data = json.loads(config.read())

        config_data["start_date"] = (datetime.now() + relativedelta(months=+1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(DISCOVER_CONFIG_FILE, "w") as fh:
            fh.write(json.dumps(config_data))

        return (
            f"{TAP_CMD} -c {DISCOVER_CONFIG_FILE} --discover"
            + ' | grep "\\"type\\": \\"SCHEMA\\"" | head -1'
            + '| jq -c "{\\"streams\\":[{\\"stream\\": .stream, \\"schema\\": .schema}]}"'
        )

    def read_cmd(self, logger: AirbyteLogger, config_path: str, catalog_path: str, state_path: str = None) -> str:
        state_flag = f"--state {state_path}" if state_path else ""
        return f"{TAP_CMD} -c {config_path} -p {catalog_path} {state_flag}"
