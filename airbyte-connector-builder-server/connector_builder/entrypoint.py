#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import asyncio
import json
import sys

from connector_builder.generated.models.stream_read_request_body import StreamReadRequestBody
from connector_builder.generated.models.streams_list_request_body import StreamsListRequestBody
from impl.default_api import DefaultApiImpl

op = sys.argv[1]
arg = sys.argv[2]

api = DefaultApiImpl()

if op == "read":
    print(asyncio.run(api.read_stream(StreamReadRequestBody.parse_obj(json.loads(arg)))))
elif op == "list":
    print(asyncio.run(api.list_streams(StreamsListRequestBody.parse_obj(json.loads(arg)))))
else:
    print("error")
