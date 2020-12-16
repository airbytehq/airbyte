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

from airbyte_protocol import AirbyteCatalog, AirbyteConnectionStatus, Status
from base_python import AirbyteLogger, CatalogHelper
from base_singer import SingerHelper, SingerSource


class SourceGoogleAdwordsSinger(SingerSource):
    def check_config(self, logger: AirbyteLogger, config_path: str, config: json) -> AirbyteConnectionStatus:
        try:
            # singer catalog that attempts to pull a stream ("accounts") that should always exists, though it may be empty.
            singer_check_catalog_path = os.path.abspath(os.path.dirname(__file__)) + "/singer_check_catalog.json"
            read_cmd = self.read_cmd(logger, config_path, singer_check_catalog_path)
            if SingerHelper.read(logger, read_cmd) is not None:
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
            else:
                return AirbyteConnectionStatus(status=Status.FAILED)

        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"{str(e)}")

    def discover_cmd(self, logger, config_path) -> str:
        return f"tap-adwords --config {config_path} --discover"

    def discover(self, logger: AirbyteLogger, config_container) -> AirbyteCatalog:
        catalog = super().discover(logger, config_container)
        return CatalogHelper.coerce_catalog_as_full_refresh(catalog)

    def read_cmd(self, logger, config_path, catalog_path, state_path=None) -> str:
        config_option = f"--config {config_path}"
        properties_option = f"--properties {catalog_path}"
        return f"tap-adwords {config_option} {properties_option}"

    def transform_config(self, raw_config):
        # required property in the singer tap, but seems like an implementation detail of stitch
        # https://github.com/singer-io/tap-adwords/blob/cf0c1ff7dae8503f97173a15cf8d78bf975069f8/tap_adwords/__init__.py#L963-L969
        raw_config["user_agent"] = "unknown"
        return raw_config
