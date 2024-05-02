#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from io import StringIO
from unittest.mock import Mock

import pytest
from source_iterable.components import EventsRecordExtractor, ListUsersRecordExtractor, XJsonRecordExtractor


@pytest.fixture
def mock_response():
    mock_response = Mock()
    return mock_response


def test_list_users_extraction(mock_response):
    mock_response.iter_lines.return_value = [b'user1@example.com', b'user2@example.com']

    extractor = ListUsersRecordExtractor(
        field_path=["getUsers"],
        config={},
        parameters={},
    )
    records = extractor.extract_records(mock_response)

    assert len(records) == 2
    assert records[0]["email"] == "user1@example.com"
    assert records[1]["email"] == "user2@example.com"


def test_xjson_extraction(mock_response):
    mock_response.iter_lines.return_value = [
        b'{"id": 1, "name": "Alice"}',
        b'{"id": 2, "name": "Bob"}'
    ]

    extractor = XJsonRecordExtractor(
        field_path=["users"],
        config={},
        parameters={},
    )
    records = extractor.extract_records(mock_response)

    assert len(records) == 2
    assert records[0] == {"id": 1, "name": "Alice"}
    assert records[1] == {"id": 2, "name": "Bob"}


def test_events_extraction(mock_response):
    mock_response.text = '{"itblInternal": 1, "_type": "event", "createdAt": "2024-03-21", "email": "user@example.com", "data": {"event_type": "click"}}\n' \
                         '{"_type": "event", "createdAt": "2024-03-22", "data": {"event_type": "purchase"}}'

    extractor = EventsRecordExtractor(
        field_path=["events"],
        config={},
        parameters={},
    )
    records = extractor.extract_records(mock_response)

    assert len(records) == 2
    assert records[0] == {'_type': 'event', 'createdAt': '2024-03-21', 'data': {'data': {'event_type': 'click'}}, 'email': 'user@example.com', 'itblInternal': 1}
    assert records[1] == {'_type': 'event', 'createdAt': '2024-03-22', 'data': {'data': {'event_type': 'purchase'}}, 'email': None, 'itblInternal': None}
