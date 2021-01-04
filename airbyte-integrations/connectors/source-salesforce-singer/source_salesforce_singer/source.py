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

import requests
from airbyte_protocol import AirbyteConnectionStatus, Status
from base_python import AirbyteLogger
from base_singer import SingerSource


class SourceSalesforceSinger(SingerSource):
    def check_config(self, logger: AirbyteLogger, config_path: str, config: json) -> AirbyteConnectionStatus:
        try:
            # pulled from tap-salesforce singer impl
            # https://github.com/singer-io/tap-salesforce/blob/master/tap_salesforce/salesforce/__init__.py#L295-L327
            if config["is_sandbox"]:
                login_url = "https://test.salesforce.com/services/oauth2/token"
            else:
                login_url = "https://login.salesforce.com/services/oauth2/token"

            login_body = {
                "grant_type": "refresh_token",
                "client_id": config["client_id"],
                "client_secret": config["client_secret"],
                "refresh_token": config["refresh_token"],
            }

            logger.info("Attempting login via OAuth2")

            r = None
            try:
                logger.info(f"Making POST request to {login_url} with body {login_body}")
                headers = {"Content-Type": "application/x-www-form-urlencoded"}
                r = requests.post(login_url, headers=headers, data=login_body)
                if r.status_code == 200:
                    logger.info("OAuth2 login successful")
                    return AirbyteConnectionStatus(status=Status.SUCCEEDED)
                else:
                    return AirbyteConnectionStatus(status=Status.FAILED, message="Response from Salesforce: {}".format(r.text))

            except Exception as e:
                error_message = str(e)
                if r is None and hasattr(e, "response") and e.response is not None:  # pylint:disable=no-member
                    r = e.response  # pylint:disable=no-member
                # NB: requests.models.Response is always falsy here. It is false if status code >= 400
                if isinstance(r, requests.models.Response):
                    error_message = error_message + ", Response from Salesforce: {}".format(r.text)
                return AirbyteConnectionStatus(status=Status.FAILED, message=error_message)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"{str(e)}")

    def discover_cmd(self, logger, config_path) -> str:
        return f"tap-salesforce --config {config_path} --discover"

    def read_cmd(self, logger, config_path, catalog_path, state_path=None) -> str:
        config_option = f"--config {config_path}"
        properties_option = f"--properties {catalog_path}"
        state_option = f"--state {state_path}" if state_path else ""
        return f"tap-salesforce {config_option} {properties_option} {state_option}"

    def transform_config(self, raw_config):
        # the select_fields_by_default is opinionated about schema changes. we want to reserve the right for the
        # Airbyte system to handle these changes, instead of the singer source.
        # todo (cgardens) - this is supposed to be handled in the ui and the api but neither of them are able to
        #  handle it right now. issue: https://github.com/airbytehq/airbyte/issues/892
        rendered_config = {
            "is_sandbox": False,
            **raw_config,
            "select_fields_by_default": True
        }
        return rendered_config
