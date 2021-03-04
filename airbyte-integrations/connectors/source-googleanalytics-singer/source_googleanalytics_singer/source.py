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
import pkgutil
from pathlib import Path
from typing import List

from base_singer import AirbyteLogger, BaseSingerSource
from jsonschema.validators import Draft4Validator
from tap_google_analytics import GAClient


class GoogleAnalyticsSingerSource(BaseSingerSource):
    """
    Google Analytics API Reference: https://developers.google.com/analytics
    """

    tap_cmd = "tap-google-analytics"
    tap_name = "Google Analytics API"
    api_error = Exception

    # can be overridden to change an input config
    def configure(self, raw_config: json, temp_dir: str) -> json:
        credentials = os.path.join(temp_dir, "credentials.json")
        with open(credentials, "w") as fh:
            fh.write(raw_config["credentials_json"])
        raw_config["key_file_location"] = credentials
        return super().configure(raw_config, temp_dir)

    def _validate_custom_reports(self, custom_reports_data: List[dict]):
        custom_reports_schema = json.loads(pkgutil.get_data("source_googleanalytics_singer", "custom_reports_schema.json"))
        if not Draft4Validator(custom_reports_schema).is_valid(custom_reports_data):
            error_messages = []
            for error in Draft4Validator(custom_reports_schema).iter_errors(custom_reports_data):
                error_messages.append(error.message)
            raise Exception("An error occurred during custom_reports data validation: " + "; ".join(error_messages))

    def _get_reports_file_path(self, temp_dir: str, custom_reports_data: List[dict]) -> str:
        report_definition = (
            json.loads(pkgutil.get_data("tap_google_analytics", "defaults/default_report_definition.json")) + custom_reports_data
        )
        custom_reports = os.path.join(temp_dir, "custom_reports.json")
        with open(custom_reports, "w") as file:
            file.write(json.dumps(report_definition))
        return custom_reports

    def _check_custom_reports(self, config: dict = None, config_path: str = None):
        if config_path:
            config = self.read_config(config_path)

        custom_reports = config.pop("custom_reports")
        if custom_reports.strip() and json.loads(custom_reports):
            custom_reports_data = json.loads(custom_reports)
            self._validate_custom_reports(custom_reports_data)
            credentials_path = Path(config["key_file_location"])
            config["reports"] = self._get_reports_file_path(credentials_path.parent, custom_reports_data)

        if config_path:
            self.write_config(config, config_path)

    def transform_config(self, raw_config: json):
        config = {
            "key_file_location": raw_config["key_file_location"],
            "view_id": raw_config["view_id"],
            "start_date": raw_config["start_date"],
            "custom_reports": raw_config.get("custom_reports", ""),
        }
        return config

    def try_connect(self, logger: AirbyteLogger, config: json):
        with open(config["key_file_location"], "r") as file:
            contents = file.read()
        client_secrets = json.loads(contents)
        additional_fields = {"end_date": "2050-10-01T00:00:00Z", "client_secrets": client_secrets}
        augmented_config = dict(additional_fields, **config)
        client = GAClient(augmented_config)
        client.fetch_metadata()
        try:
            self._check_custom_reports(config=config)
        except Exception as e:
            raise Exception(f"Custom Reports format is incorrect: {e}")

    def discover_cmd(self, logger: AirbyteLogger, config_path: str) -> str:
        self._check_custom_reports(config_path=config_path)
        return f"{self.tap_cmd} --config {config_path} --discover"
