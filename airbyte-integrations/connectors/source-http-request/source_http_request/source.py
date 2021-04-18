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
from datetime import datetime
from typing import Dict, Generator

import requests
from airbyte_protocol import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)
from base_python import AirbyteLogger, Source


class SourceHttpRequest(Source):
    STREAM_NAME = "data"

    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        r = self._make_request(config)
        if r.status_code == 200:
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        else:
            return AirbyteConnectionStatus(status=Status.FAILED, message=r.text)

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "additionalProperties": True,
            "type": "object",
            # todo (cgardens) - remove data column. added to handle UI bug where streams without fields cannot be selected.
            # issue: https://github.com/airbytehq/airbyte/issues/1104
            "properties": {"data": {"type": "object"}},
        }

        # json body will be returned as the "data" stream". we can't know its schema ahead of time, so we assume it's object (i.e. valid json).
        return AirbyteCatalog(streams=[AirbyteStream(name=SourceHttpRequest.STREAM_NAME, json_schema=json_schema)])

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:
        r = self._make_request(config)
        if r.status_code != 200:
            raise Exception(f"Request failed. {r.text}")

        # need to eagerly fetch the json.
        message = AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream=SourceHttpRequest.STREAM_NAME, data=r.json(), emitted_at=int(datetime.now().timestamp()) * 1000
            ),
        )

        return (m for m in [message])

    def _make_request(self, config):
        parsed_config = self._parse_config(config)
        http_method = parsed_config.get("http_method").lower()
        url = parsed_config.get("url")
        headers = parsed_config.get("headers", {})
        body = parsed_config.get("body", {})

        if http_method == "get":
            r = requests.get(url, headers=headers, json=body)
        elif http_method == "post":
            r = requests.post(url, headers=headers, json=body)
        else:
            raise Exception(f"Did not recognize http_method: {http_method}")

        return r

    # visible / separated for testing
    def _parse_config(self, config):
        return {
            "url": config.get("url"),
            "http_method": config["http_method"],
            "headers": json.loads(config.get("headers", "{}")),
            "body": json.loads(config.get("body", "{}")),
        }
