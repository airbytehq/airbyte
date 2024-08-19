#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import io

import requests
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonlDecoder
from source_iterable.components import EventsRecordExtractor


def test_events_extraction():
    mock_response = requests.Response()
    mock_response.raw = io.BytesIO(
        b'{"itblInternal": 1, "_type": "event", "createdAt": "2024-03-21", "email": "user@example.com", "data": {"event_type": "click"}}\n{"_type": "event", "createdAt": "2024-03-22", "data": {"event_type": "purchase"}}'
    )

    extractor = EventsRecordExtractor(
        field_path=[],
        decoder=JsonlDecoder(parameters={}),
        config={},
        parameters={},
    )
    records = list(extractor.extract_records(mock_response))

    assert len(records) == 2
    assert records[0] == {
        "_type": "event",
        "createdAt": "2024-03-21",
        "data": {"data": {"event_type": "click"}},
        "email": "user@example.com",
        "itblInternal": 1,
    }
    assert records[1] == {
        "_type": "event",
        "createdAt": "2024-03-22",
        "data": {"data": {"event_type": "purchase"}},
        "email": None,
        "itblInternal": None,
    }
