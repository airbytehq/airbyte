#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from connector_builder.generated.apis.default_api_interface import DefaultApi
from connector_builder.generated.models.stream_read import StreamRead
from connector_builder.generated.models.stream_read_request_body import StreamReadRequestBody
from connector_builder.generated.models.streams_list_read import StreamsListRead
from connector_builder.generated.models.streams_list_request_body import StreamsListRequestBody
from fastapi import Body


class DefaultApiImpl(DefaultApi):
    async def get_manifest_template(self) -> str:
        return "Hello World"

    async def list_streams(self, streams_list_request_body: StreamsListRequestBody = Body(None, description="")) -> StreamsListRead:
        raise Exception("not yet implemented")

    async def read_stream(self, stream_read_request_body: StreamReadRequestBody = Body(None, description="")) -> StreamRead:
        raise Exception("not yet implemented")
