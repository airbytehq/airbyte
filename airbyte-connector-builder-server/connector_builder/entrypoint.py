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
    response = asyncio.run(api.read_stream(StreamReadRequestBody.parse_obj(json.loads(arg))))
    logs = [{"message": l["message"].replace("'", "")} for l in response.logs]
    slices = response.slices
    slice = slices[0]  # hack: only return first slice
    pages = [
        {"records": p.records,
         "request": {"url": p.request.url, "http_method": p.request.http_method, "parameters": p.request.parameters or {},
                     "body": p.request.body or {}, "headers": p.request.body or {}},
         "response": {"status": p.response.status,
                      "body": {k: v.replace("'", "") for k, v in p.response.body.items()} if p.response.body else {}}}
        for p in slice.pages]
    print({"logs": logs, "slices": [{"pages": pages}]})
elif op == "list":
    try:
        response = asyncio.run(api.list_streams(StreamsListRequestBody.parse_obj(json.loads(arg))))
        streams = [json.dumps(vars(s)) for s in response.streams]
        print({"streams": streams})
    except Exception as e:
        print({"streams": []})
else:
    print(f"op: {op}")
=======
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(initialize_router(DefaultApiImpl(LowCodeSourceAdapter)))
>>>>>>> master
