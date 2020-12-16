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

from airbyte_protocol import AirbyteCatalog, AirbyteConnectionStatus, Status
from base_python import AirbyteLogger, CatalogHelper
from base_singer import SingerSource

TAP_CMD = "tap-facebook"


class SourceFacebookMarketingApiSinger(SingerSource):
    def transform_config(self, raw_config: json) -> json:
        # todo (cgardens) - this is supposed to be handled in the ui and the api but neither of them are able to handle it right now. issue: https://github.com/airbytehq/airbyte/issues/892
        return {
            "start_date": raw_config["start_date"],
            "account_id": raw_config["account_id"],
            "access_token": raw_config["access_token"],
            # tap-singer expects a string not a boolean
            "include_deleted": str(raw_config.get("include_deleted", True)),
        }

    def check_config(self, logger: AirbyteLogger, config_path: str, config: json) -> AirbyteConnectionStatus:
        try:
            self._discover_internal(logger, config)
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            # TODO parse the exception message for a human readable error
            logger.error("Exception while connecting to the FB Marketing API")
            logger.error(str(e))
            return AirbyteConnectionStatus(
                status=Status.FAILED, message="Unable to connect to the FB Marketing API with the provided credentials. "
            )

    def discover_cmd(self, logger: AirbyteLogger, config_path: str) -> str:
        return f"{TAP_CMD} -c {config_path} --discover"

    def discover(self, logger: AirbyteLogger, config_container) -> AirbyteCatalog:
        catalog = super().discover(logger, config_container)
        return CatalogHelper.coerce_catalog_as_full_refresh(catalog)

    def read_cmd(self, logger: AirbyteLogger, config_path: str, catalog_path: str, state_path: str = None) -> str:
        # Don't pass in state since this tap does not respect replication_method singer key
        return f"{TAP_CMD} -c {config_path} -p {catalog_path}"
