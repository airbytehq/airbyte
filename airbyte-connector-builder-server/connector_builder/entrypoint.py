#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import asyncio
import json
import sys

from connector_builder.generated.models.http_request import HttpRequest
from connector_builder.generated.models.http_response import HttpResponse
from connector_builder.generated.models.stream_read import StreamRead
from connector_builder.generated.models.stream_read_pages import StreamReadPages
from connector_builder.generated.models.stream_read_slices import StreamReadSlices
from connector_builder.generated.models.streams_list_request_body import StreamsListRequestBody
from connector_builder.impl.default_api import DefaultApiImpl
from connector_builder.impl.low_code_cdk_adapter import LowCodeSourceAdapterFactory

op = sys.argv[1]
arg = sys.argv[2]

_MAXIMUM_NUMBER_OF_PAGES_PER_SLICE = 5
_MAXIMUM_NUMBER_OF_SLICES = 5
_ADAPTER_FACTORY = LowCodeSourceAdapterFactory(_MAXIMUM_NUMBER_OF_PAGES_PER_SLICE, _MAXIMUM_NUMBER_OF_SLICES)
api = DefaultApiImpl(_ADAPTER_FACTORY, _MAXIMUM_NUMBER_OF_PAGES_PER_SLICE, _MAXIMUM_NUMBER_OF_SLICES)

if op == "read":
    records = [{"id": 0}, {"id": "1"}]
    request = HttpRequest(url="https://pokeapi", http_method="GET")
    http_response = HttpResponse(status=200, body={}, headers={})
    response = StreamRead(
        logs=[], slices=[StreamReadSlices(pages=[StreamReadPages(records=records, request=request, response=http_response)])]
    )
    # response = asyncio.run(api.read_stream(StreamReadRequestBody.parse_obj(json.loads(arg))))
    logs = [{"message": log["message"].replace("'", "")} for log in response.logs]
    slices = response.slices
    slice = slices[0]  # hack: only return first slice
    pages = [
        {
            "records": p.records,
            "request": {
                "url": p.request.url,
                "http_method": p.request.http_method,
                "parameters": p.request.parameters or {},
                "body": p.request.body or {},
                "headers": p.request.body or {},
            },
            "response": {
                "status": p.response.status,
                "body": {k: v.replace("'", "") for k, v in p.response.body.items()} if p.response.body else {},
            },
        }
        for p in slice.pages
    ]
    print({"logs": logs, "slices": [{"pages": pages}]})
elif op == "list":
    try:
        response = asyncio.run(api.list_streams(StreamsListRequestBody.parse_obj(json.loads(arg))))
        streams = [json.dumps(vars(s)) for s in response.streams]
        print({"streams": streams})
    except Exception:
        print({"streams": []})
else:
    print(f"op: {op}")
