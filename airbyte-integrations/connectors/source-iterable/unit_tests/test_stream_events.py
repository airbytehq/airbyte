#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import pytest
import requests
import responses
import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.types import StreamSlice
from source_iterable.source import SourceIterable


@responses.activate
@pytest.mark.parametrize(
    "response_objects,expected_objects,jsonl_body",
    [
        (
                [
                    {
                        "createdAt": "2021",
                        "signupSource": "str",
                        "emailListIds": [1],
                        "itblInternal": {"documentUpdatedAt": "2021", "documentCreatedAt": "202"},
                        "_type": "str",
                        "messageTypeIds": [],
                        "channelIds": [],
                        "email": "test@mail.com",
                        "profileUpdatedAt": "2021",
                    }
                ],
                [
                    {
                        "itblInternal": {"documentUpdatedAt": "2021", "documentCreatedAt": "202"},
                        "_type": "str",
                        "createdAt": "2021",
                        "email": "test@mail.com",
                        "data": {
                            "signupSource": "str",
                            "emailListIds": [1],
                            "messageTypeIds": [],
                            "channelIds": [],
                            "profileUpdatedAt": "2021",
                        },
                    }
                ],
                True,
        )
    ],
)
def test_events_parse_response(response_objects, expected_objects, jsonl_body, config):
    if jsonl_body:
        response_body = "\n".join([json.dumps(obj) for obj in response_objects])
    else:
        response_body = json.dumps(response_objects)

    responses.add(
        responses.GET,
        "https://api.iterable.com/api/export/userEvents?includeCustomEvents=true&email=user1",
        body=response_body
    )

    response = requests.get("https://api.iterable.com/api/export/userEvents?includeCustomEvents=true&email=user1")

    stream = next(filter(lambda x: x.name == "events", SourceIterable().streams(config=config)))

    if jsonl_body:
        stream_slice = StreamSlice(partition={'email': 'user1', 'parent_slice': {'list_id': 111111, 'parent_slice': {}}}, cursor_slice={})
        records = list(map(lambda record: record.data, stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)))
        assert records == expected_objects
    else:
        with pytest.raises(TypeError):
            [record for record in stream.retriever._parse_response(response)]
