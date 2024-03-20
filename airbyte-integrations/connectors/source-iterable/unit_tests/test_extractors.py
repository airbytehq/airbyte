#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from io import StringIO
from unittest.mock import Mock

import pytest
from source_iterable.components import (  # Import your module containing the classes
    EventsRecordExtractor,
    ListUsersRecordExtractor,
    XJsonRecordExtractor,
)


@pytest.fixture
def mock_response():
    mock_response = Mock()
    return mock_response

@pytest.mark.parametrize("extractor_class,field_path", [(ListUsersRecordExtractor, "getUsers"), (XJsonRecordExtractor, "users"), (EventsRecordExtractor, "events")])
def test_extract_records(mock_response, extractor_class, field_path):
    # Prepare mock response data for each extractor
    if extractor_class == ListUsersRecordExtractor:
        mock_response.iter_lines.return_value = [b'user1@example.com', b'user2@example.com']
    elif extractor_class == XJsonRecordExtractor:
        mock_response.iter_lines.return_value = [
            b'{"id": 1, "name": "Alice"}',
            b'{"id": 2, "name": "Bob"}'
        ]
    elif extractor_class == EventsRecordExtractor:
        mock_response.text = '{"itblInternal": 1, "_type": "event", "createdAt": "2024-03-21", "email": "user@example.com", "data": {"event_type": "click"}}\n' \
                            '{"_type": "event", "createdAt": "2024-03-22", "data": {"event_type": "purchase"}}'
    else:
        raise ValueError("Unknown extractor class")

    # Instantiate extractor and run test
    extractor = extractor_class(
        field_path=[field_path],
        config={},
        parameters={},
    )
    records = extractor.extract_records(mock_response)

    # Validate the records
    if extractor_class == ListUsersRecordExtractor:
        assert len(records) == 2
        assert records[0]["email"] == "user1@example.com"
        assert records[1]["email"] == "user2@example.com"
    elif extractor_class == XJsonRecordExtractor:
        assert len(records) == 2
        assert records[0] == {"id": 1, "name": "Alice"}
        assert records[1] == {"id": 2, "name": "Bob"}
    elif extractor_class == EventsRecordExtractor:
        assert len(records) == 2
        assert records[0] == {'_type': 'event', 'createdAt': '2024-03-21', 'data': {'data': {'event_type': 'click'}}, 'email': 'user@example.com', 'itblInternal': 1}
        assert records[1] == {'_type': 'event', 'createdAt': '2024-03-22', 'data': {'data': {'event_type': 'purchase'}}, 'email': None, 'itblInternal': None}
    else:
        raise ValueError("Unknown extractor class")
