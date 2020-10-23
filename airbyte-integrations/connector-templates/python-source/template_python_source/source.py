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

import pkgutil
import time
from typing import Generator

from airbyte_protocol import AirbyteCatalog, AirbyteCheckResponse, AirbyteMessage, AirbyteRecordMessage, AirbyteStateMessage, Source


class TemplatePythonSource(Source):
    def __init__(self):
        pass

    def check(self, logger, config_container) -> AirbyteCheckResponse:
        logger.info(f"Checking configuration ({config_container.rendered_config_path})...")
        return AirbyteCheckResponse(True, {})

    def discover(self, logger, config_container) -> AirbyteCatalog:
        logger.info(f"Discovering ({config_container.rendered_config_path})...")
        return AirbyteCatalog.from_json(pkgutil.get_data(__name__, "catalog.json"))

    def read(self, logger, config_container, catalog_path, state_path=None) -> Generator[AirbyteMessage, None, None]:
        logger.info(f"Reading ({config_container.rendered_config_path}, {catalog_path}, {state_path})...")

        message = AirbyteRecordMessage(stream="love_airbyte", data={"love": True}, emitted_at=int(time.time() * 1000))
        yield AirbyteMessage(type="RECORD", record=message)

        state = AirbyteStateMessage(data={"love_cursor": "next_version"})
        yield AirbyteMessage(type="STATE", state=state)
