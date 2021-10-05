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
from genson import SchemaBuilder
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
import sys,re
sys.path.insert(0, '/home/charity/airbyte/airbyte-integrations/connectors/source-corebos/')
from source_corebos.libs.WSClient import *


class SourceCorebos(Source):
    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        url = config["url"]
        client = WSClient(url)
        username = config["username"]
        key = config["access_token"]
        logger.info(username)
        logger.info(key)
        login = client.do_login(username,key,withpassword=False)
        logger.info(login)
        if login:
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        else:
            return AirbyteConnectionStatus(
                    status=Status.FAILED,
                    message='An exception occurred, content: {}'.format(login),
                )

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        url = config["url"]
        username = config["username"]
        key = config["access_token"]
        # skip
        structure = open('catalog.json',)
        dataschema = json.load(structure)
        # goon
        client = WSClient(url)
        login = client.do_login(username,key,withpassword=False)
        if login:
            result = client.do_listtypes
        streams = []
        for stream_name in result["types"]:
            builder = SchemaBuilder()
            builder.add_schema({"type": "object", "properties": {}})
            for one in dataschema["streams"]:
                if one["name"] == stream_name:
                    object_schema = one
            builder.add_object(object_schema)
            json_schema = builder.to_json(indent=2)
            streams.append(AirbyteStream(name=stream_name, json_schema=json_schema))
        structure.close()
        return AirbyteCatalog(streams=streams)

    

    def read(self, logger: AirbyteLogger, config: json, catalog:ConfiguredAirbyteCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:

        logger.info("read called")

        url = config["url"]
        username = config["username"]
        key = config["access_token"]
        retrieve_stream = config["query"]
        retrieve_stream = re.search('(?<=from )(\w+)',retrieve_stream).group(1)

        client = WSClient(url)
        login = client.do_login(username,key,withpassword=False)
        query = config["query"]
        logger.info(query)

        if login:
            data = client.do_query(query)
        else:
            logger.info("authentication failed: {}",login)

        try:
            for single_dict in data:    
                yield AirbyteMessage(
                    type=Type.RECORD,
                    record=AirbyteRecordMessage(stream=retrieve_stream, data=single_dict, emitted_at=int(datetime.now().timestamp()) * 1000),
                )
        except Exception as err:
            reason = f"Failed to read data of {retrieve_stream} at {url}"
            logger.error(reason)
            raise err
