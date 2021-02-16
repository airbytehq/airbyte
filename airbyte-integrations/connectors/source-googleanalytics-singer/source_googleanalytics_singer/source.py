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
    _custom_reports_schema = {
        "$schema": "http://json-schema.org/schema#",
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "dimensions": {
                    "type": "array",
                    "title": "dimensions",
                    "items": {
                        "type": "string",
                        "enum": [
                            "ga:browser",
                            "ga:city",
                            "ga:continent",
                            "ga:country",
                            "ga:date",
                            "ga:deviceCategory",
                            "ga:hostname",
                            "ga:medium",
                            "ga:metro",
                            "ga:operatingSystem",
                            "ga:pagePath",
                            "ga:region",
                            "ga:socialNetwork",
                            "ga:source",
                            "ga:subContinent",
                        ],
                    },
                    "maxItems": 7,
                    "uniqueItems": True,
                },
                "metrics": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "ga:14dayUsers",
                            "ga:1dayUsers",
                            "ga:28dayUsers",
                            "ga:30dayUsers",
                            "ga:7dayUsers",
                            "ga:avgSessionDuration",
                            "ga:avgTimeOnPage",
                            "ga:bounceRate",
                            "ga:entranceRate",
                            "ga:entrances",
                            "ga:exitRate",
                            "ga:exits",
                            "ga:newUsers",
                            "ga:pageviews",
                            "ga:pageviewsPerSession",
                            "ga:sessions",
                            "ga:sessionsPerUser",
                            "ga:uniquePageviews",
                            "ga:users",
                        ],
                    },
                    "maxItems": 10,
                    "uniqueItems": True,
                },
            },
        },
    }

    # can be overridden to change an input config
    def configure(self, raw_config: json, temp_dir: str) -> json:
        credentials = os.path.join(temp_dir, "credentials.json")
        with open(credentials, "w") as fh:
            fh.write(raw_config["credentials_json"])
        raw_config["key_file_location"] = credentials
        if raw_config["custom_reports"].strip() and json.loads(raw_config["custom_reports"]):
            custom_reports_data = json.loads(raw_config["custom_reports"])
            if not Draft4Validator(self._custom_reports_schema).is_valid(custom_reports_data):
                error_messages = []
                for error in Draft4Validator(self._custom_reports_schema).iter_errors(custom_reports_data):
                    error_messages.append(error.message)
                raise Exception("Schema not validate custom reports data with error(s):\n" + ";\n".join(error_messages))

            report_definition = (
                json.loads(pkgutil.get_data("tap_google_analytics", "defaults/default_report_definition.json")) + custom_reports_data
            )
            custom_reports = os.path.join(temp_dir, "custom_reports.json")
            with open(custom_reports, "w") as file:
                file.write(json.dumps(report_definition))
            raw_config["reports"] = custom_reports
        return super().configure(raw_config, temp_dir)

    def transform_config(self, raw_config: json):
        config = {
            "key_file_location": raw_config["key_file_location"],
            "view_id": raw_config["view_id"],
            "start_date": raw_config["start_date"],
        }
        if raw_config.get("reports"):
            config["reports"] = raw_config["reports"]
        return config

    def try_connect(self, logger: AirbyteLogger, config: json):
        with open(config["key_file_location"], "r") as file:
            contents = file.read()
        client_secrets = json.loads(contents)
        additional_fields = {"end_date": "2050-10-01T00:00:00Z", "client_secrets": client_secrets}
        augmented_config = dict(additional_fields, **config)
        client = GAClient(augmented_config)
        client.fetch_metadata()
