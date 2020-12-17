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

from airbyte_protocol import AirbyteConnectionStatus, Status
from base_singer import AirbyteLogger, SingerSource
from tap_google_analytics import GAClient


class GoogleAnalyticsSingerSource(SingerSource):

    # can be overridden to change an input config
    def configure(self, raw_config: json, temp_dir: str) -> json:
        credentials = os.path.join(temp_dir, "credentials.json")
        with open(credentials, "w") as fh:
            fh.write(raw_config["credentials_json"])
        raw_config["key_file_location"] = credentials
        return super().configure(raw_config, temp_dir)

    def transform_config(self, raw_config: json):
        return {
            "key_file_location": raw_config["key_file_location"],
            "view_id": raw_config["view_id"],
            "start_date": raw_config["start_date"],
        }

    def check_config(self, logger: AirbyteLogger, config_path: str, config: json) -> AirbyteConnectionStatus:
        try:
            # this config is the one specific to GAClient, which does not match the root Singer config
            with open(config["key_file_location"], "r") as file:
                contents = file.read()
            client_secrets = json.loads(contents)
            additional_fields = {"end_date": "2050-10-01T00:00:00Z", "client_secrets": client_secrets}
            augmented_config = dict(additional_fields, **config)
            client = GAClient(augmented_config)
            client.fetch_metadata()
        except Exception as e:
            logger.error(f"Failed check with exception: {e}")
            return AirbyteConnectionStatus(status=Status.FAILED)
        else:
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def discover_cmd(self, logger, config_path) -> str:
        return f"tap-google-analytics --discover --config {config_path}"

    def read_cmd(self, logger, config_path, catalog_path, state_path=None) -> str:
        config_option = f"--config {config_path}"
        state_option = f"--state {state_path}" if state_path else ""
        return f"tap-google-analytics {config_option} {state_option}"
