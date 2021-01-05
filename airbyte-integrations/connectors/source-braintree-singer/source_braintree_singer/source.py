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
from datetime import datetime
from typing import Dict

import braintree
from airbyte_protocol import SyncMode
from base_python import AirbyteLogger
from base_singer import BaseSingerSource, SyncModeInfo
from braintree.exceptions.authentication_error import AuthenticationError
from dateutil import parser
from dateutil.relativedelta import relativedelta


class SourceBraintreeSinger(BaseSingerSource):
    tap_cmd = "tap-braintree"
    tap_name = "BrainTree API"
    api_error = AuthenticationError
    force_full_refresh = True

    def transform_config(self, raw_config: json) -> json:
        config = raw_config
        if "start_date" in raw_config:
            config["start_date"] = (parser.parse(raw_config["start_date"]) + relativedelta(months=+1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            config["start_date"] = (datetime.now() + relativedelta(months=+1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        return config

    def try_connect(self, logger: AirbyteLogger, config: json):
        """Test provided credentials, raises self.api_error if something goes wrong"""
        client = braintree.BraintreeGateway(
            braintree.Configuration(
                environment=getattr(braintree.Environment, config["environment"]),
                merchant_id=config["merchant_id"],
                public_key=config["public_key"],
                private_key=config["private_key"],
            )
        )
        client.transaction.search(braintree.TransactionSearch.created_at.between(datetime.now() + relativedelta(days=-1), datetime.now()))

    def get_sync_mode_overrides(self) -> Dict[str, SyncModeInfo]:
        return {"transactions": SyncModeInfo(supported_sync_modes=[SyncMode.incremental])}

    def discover_cmd(self, logger: AirbyteLogger, config_path: str) -> str:
        return (
            f"{self.tap_cmd} -c {config_path} --discover"
            + ' | grep "\\"type\\": \\"SCHEMA\\"" | head -1'
            + '| jq -c "{\\"streams\\":[{\\"stream\\": .stream, \\"schema\\": .schema}]}"'
        )

    def read_cmd(self, logger: AirbyteLogger, config_path: str, catalog_path: str, state_path: str = None) -> str:
        state_option = f"--state {state_path}" if state_path else ""
        return f"{self.tap_cmd} -c {config_path} -p {catalog_path} {state_option}"
