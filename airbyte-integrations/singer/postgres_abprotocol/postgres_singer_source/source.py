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

import urllib.request
import psycopg2

from typing import Generator

from airbyte_protocol import AirbyteCatalog
from airbyte_protocol import AirbyteConnectionStatus
from airbyte_protocol import Status
from airbyte_protocol import AirbyteMessage
from airbyte_protocol import Source
from airbyte_protocol import ConfigContainer
from base_singer import SingerHelper, SingerSource


TAP_CMD = "PGCLIENTENCODING=UTF8 tap-postgres"
class PostgresSingerSource(SingerSource):
    def __init__(self):
        pass

    def check(self, logger, config_container: ConfigContainer) -> AirbyteConnectionStatus:
        config = config_container.rendered_config
        try:
            params="dbname='{dbname}' user='{user}' host='{host}' password='{password}' port='{port}'".format(**config)
            psycopg2.connect(params)
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            logger.error(f"Exception while connecting to postgres database: {e}")
            return AirbyteConnectionStatus(status=Status.FAILED, message=str(e))

    def transform_config(self, raw_config):
        # the filter_dbs option is not required input but is a significant performance improvement on shared DB clusters e.g: Heroku free tier.
        # It should be equal to the dbname option in all cases.
        # See https://github.com/singer-io/tap-postgres source code for more information
        rendered_config = dict(raw_config)
        rendered_config['filter_dbs'] = raw_config['dbname']
        return rendered_config

    def discover_cmd(self, logger, config_path) -> AirbyteCatalog:
        return f"{TAP_CMD} --config {config_path} --discover"

    def read_cmd(self, logger, config_path, catalog_path, state_path=None) -> Generator[AirbyteMessage, None, None]:
        catalog_option = f"--properties {catalog_path}"
        config_option = f"--config {config_path}"
        state_option = f"--state {state_path}" if state_path else ""
        return f"{TAP_CMD} {catalog_option} {config_option} {state_option}"
