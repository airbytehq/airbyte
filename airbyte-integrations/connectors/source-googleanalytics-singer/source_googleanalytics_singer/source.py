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

from airbyte_protocol import AirbyteConnectionStatus, Status
from base_singer import SingerSource
from tap_google_analytics import GAClient

CREDENTIALS_FILE = os.path.join(tempfile.gettempdir(), "credentials.json")


class GoogleAnalyticsSingerSource(SingerSource):
    def __init__(self):
        pass

    def check(self, logger, config_container) -> AirbyteConnectionStatus:
        try:
            # this config is the one specific to GAClient, which does not match the root Singer config
            client_secrets = json.loads(config_container.raw_config["credentials_json"])
            additional_fields = {"end_date": "2050-10-01T00:00:00Z", "client_secrets": client_secrets}
            augmented_config = dict(additional_fields, **config_container.rendered_config)
            client = GAClient(augmented_config)
            client.fetch_metadata()
        except Exception as e:
            logger.error(f"Failed check with exception: {e}")
            return AirbyteConnectionStatus(status=Status.FAILED)
        else:
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def transform_config(self, raw_config):
        with open(CREDENTIALS_FILE, "w") as fh:
            fh.write(raw_config["credentials_json"])

        return {"key_file_location": CREDENTIALS_FILE, "view_id": raw_config["view_id"], "start_date": raw_config["start_date"]}

    def discover_cmd(self, logger, config_path) -> str:
        return f"tap-google-analytics --discover --config {config_path}"

    def read_cmd(self, logger, config_path, catalog_path, state_path=None) -> str:
        config_option = f"--config {config_path}"
        state_option = f"--state {state_path}" if state_path else ""
        return f"tap-google-analytics {config_option} {state_option}"
