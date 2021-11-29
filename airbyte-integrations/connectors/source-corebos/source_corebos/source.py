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
from source_corebos.libs.WSClient import *

DATASET_ITEMS_STREAM_NAME = "DatasetItems"

BATCH_SIZE = 50000


class SourceCorebos(Source):
    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        url = config["url"]
        client = WSClient(url)
        username = config["username"]
        key = config["access_token"]
        login = client.do_login(username,key)
        if login:
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        else:
            return AirbyteConnectionStatus(
                    status=Status.FAILED,
                    message='An exception occurred, content: {}'.format(login),
                )

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        stream_name = DATASET_ITEMS_STREAM_NAME
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
        }
        return AirbyteCatalog(
            streams=[AirbyteStream(name=stream_name, json_schema=json_schema)]
        )

    

    def read(self, logger: AirbyteLogger, config: json, catalog:ConfiguredAirbyteCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:

        logger.info("read called")

        url = config["url"]
        username = config["username"]
        key = config["access_token"]
        client = WSClient(url)
        login = client.do_login(username,key,withpassword=False)
        query = config["query"]
        logger.info(query)
        data = client.do_query(query)
        try:
            for single_dict in data:    
                yield AirbyteMessage(
                    type=Type.RECORD,
                    record=AirbyteRecordMessage(stream=DATASET_ITEMS_STREAM_NAME, data=single_dict, emitted_at=int(datetime.now().timestamp()) * 1000),
                )
        except Exception as err:
            reason = f"Failed to read data of {DATASET_ITEMS_STREAM_NAME} at {url}"
            logger.error(reason)
            raise err
