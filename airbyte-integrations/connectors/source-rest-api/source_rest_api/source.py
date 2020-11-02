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

from typing import Generator
import requests
from datetime import datetime

from airbyte_protocol import AirbyteCatalog, AirbyteStream, AirbyteConnectionStatus, AirbyteMessage, Status, AirbyteRecordMessage
from base_python import AirbyteLogger, Source


class SourceRestApi(Source):
    def __init__(self):
        super().__init__()

    def check(self, logger: AirbyteLogger, config_container) -> AirbyteConnectionStatus:
        r = self._make_request(config_container.rendered_config)
        if r.status_code == 200:
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        else:
            return AirbyteConnectionStatus(status=Status.FAILED, message=r.text)

    def discover(self, logger: AirbyteLogger, config_container) -> AirbyteCatalog:
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "additionalProperties": True,
            "type": "object"
        }

        # json body will be returned as the "data" stream". we can't know its schema ahead of time, so we assume it's object (i.e. valid json).
        return AirbyteCatalog(streams=[AirbyteStream(name="data", json_schema=json_schema)])

    def read(self, logger: AirbyteLogger, config_container, catalog_path, state=None) -> Generator[AirbyteMessage, None, None]:
        r = self._make_request(config_container.rendered_config)
        return AirbyteRecordMessage(stream="data", data=r.json, emitted_at=int(datetime.now().timestamp()) * 1000)

    def _make_request(self, config):
        url = config.get("url")
        http_method = config["http_method"]
        headers = config.get("headers", {})
        body = config.get("body", {})

        if http_method == "get":
            r = requests.get(url, headers=headers, data=body)
        elif http_method == "post":
            r = requests.post(url, headers=headers, data=body)
        else:
            raise Exception(f"Did not recognize http_method: {http_method}")

        return r
