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
from base_singer import AirbyteLogger, SingerSource
from requests.status_codes import codes as status_codes


class SourceHubspotSinger(SingerSource):
    def check_config(self, logger: AirbyteLogger, config_path: str, config: json) -> AirbyteConnectionStatus:
        error_msg = "Unable to connect with the provided credentials. Error: {}"
        try:
            api_key = config.get("hapikey")
            if api_key:
                logger.info("checking with api key")
                r = requests.get(f"https://api.hubapi.com/contacts/v1/lists/all/contacts/all?hapikey={api_key}")
            else:
                logger.info("checking with oauth")
                # borrowing from tap-hubspot
                # https://github.com/singer-io/tap-hubspot/blob/master/tap_hubspot/__init__.py#L208-L229
                payload = {
                    "grant_type": "refresh_token",
                    "redirect_uri": config["redirect_uri"],
                    "refresh_token": config["refresh_token"],
                    "client_id": config["client_id"],
                    "client_secret": config["client_secret"],
                }
                resp = requests.post("https://api.hubapi.com/oauth/v1/token", data=payload)

                if resp.status_code == status_codes.FORBIDDEN:
                    return AirbyteConnectionStatus(status=Status.FAILED, message=error_msg.format(resp.text))

                try:
                    resp.raise_for_status()
                except Exception as e:
                    logger.error(str(e))
                    return AirbyteConnectionStatus(status=Status.FAILED, message=error_msg.format(e))

                auth = resp.json()
                headers = {"Authorization": "Bearer {}".format(auth["access_token"])}

                r = requests.get("https://api.hubapi.com/contacts/v1/lists/all/contacts/all", headers=headers)

            if r.status_code == status_codes.OK:
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
            else:
                return AirbyteConnectionStatus(status=Status.FAILED, message=error_msg.format(r.text))
        except Exception as e:
            logger.error(str(e))
            return AirbyteConnectionStatus(status=Status.FAILED, message=error_msg.format(e))

    def discover_cmd(self, logger, config_path) -> str:
        return f"tap-hubspot --config {config_path} --discover"

    def read_cmd(self, logger, config_path, catalog_path, state_path=None) -> str:
        config_option = f"--config {config_path}"
        properties_option = f"--properties {catalog_path}"
        state_option = f"--state {state_path}" if state_path else ""
        return f"tap-hubspot {config_option} {properties_option} {state_option}"

    def transform_config(self, raw_config):
        rendered_config = dict(raw_config)
        singer_config = dict()

        # the singer integration requires if the hapikey field is passed that all
        # of the oauth fields get passed as well. it just checks existence. we
        # do not bother our users to provide the extra oauth creds if they are
        # using an api key. so we fill them in with dummy values for them.
        if "api_key" in rendered_config["credentials"]:
            singer_config["hapikey"] = rendered_config["credentials"]["api_key"]
            singer_config["redirect_uri"] = "placeholder"
            singer_config["client_id"] = "placeholder"
            singer_config["client_secret"] = "placeholder"
            singer_config["refresh_token"] = "placeholder"
        else:
            singer_config = rendered_config["credentials"]

        singer_config["start_date"] = rendered_config["start_date"]
        # always turn off singer tracking.
        singer_config["disable_collection"] = True

        return singer_config
