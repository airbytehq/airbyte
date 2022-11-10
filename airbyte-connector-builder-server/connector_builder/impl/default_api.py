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
        return {
            "streams": [
                {"name": "disputes", "url": "http://api.com/disputes"},
                {"name": "transactions", "url": "http://api.com/transactions"},
                {"name": "users", "url": "http://api.com/users"}
            ]
        }

    async def read_stream(self, stream_read_request_body: StreamReadRequestBody = Body(None, description="")) -> StreamRead:
        return {
            "logs": [
                {"level": "INFO", "message": "Syncing stream disputes!!"},
                {"level": "INFO", "message": "Setting state of disputes to {'date': '2022-09-25'} !!"}
            ],
            "slices": [
                {
                    "sliceDescriptor": {
                        "startDatetime": "1 Jan 2022",
                        "listItem": "airbyte-cloud"
                    },
                    "state": {
                        "type": "STREAM",
                        "stream": {
                            "stream_descriptor": {
                                "name": "disputes"
                            },
                            "stream_state": {
                                "date": "2022-01-01"
                            }
                        },
                        "data": {
                            "disputes": {
                                "date": "2022-01-01"
                            }
                        }
                    },
                    "pages": [
                        {
                            "records": [
                                {
                                    "id": "day_1_page_1_record_1",
                                    "object": "disputes",
                                    "amount": 1000
                                },
                                {
                                    "id": "day_1_page_1_record_2",
                                    "object": "disputes",
                                    "amount": 2000
                                },
                                {
                                    "id": "day_1_page_1_record_3",
                                    "object": "disputes",
                                    "amount": 3000
                                }
                            ],
                            "request": {
                                "url": "https://api.com/disputes?page=1",
                                "headers": {
                                    "Accept": "*/*",
                                    "Accept-Encoding": "gzip, deflate, br",
                                    "Accept-Language": "en-US,en;q=0.9",
                                    "Cache-Control": "no-cache",
                                    "Connection": "keep-alive"
                                },
                                "parameters": {
                                    "page": 1
                                }
                            },
                            "response": {
                                "status": 200,
                                "headers": {
                                    "Content-Type": "application/json",
                                    "Content-Length": "2626",
                                    "Connection": "keep-alive",
                                    "cache-control": "no-cache, no-store"
                                },
                                "body": {
                                    "data": {}
                                },
                            }
                        }
                    ]
                }
            ]
        }
