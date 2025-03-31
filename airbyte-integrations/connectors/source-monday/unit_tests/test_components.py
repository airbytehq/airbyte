#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any

import pytest
from requests import Response
from source_monday.extractor import MondayIncrementalItemsExtractor
from source_monday.state_migration import MondayStateMigration


@pytest.mark.parametrize(
    "input_state, expected_state, expected_should_migrate",
    [
        # Test case 1: State with activity_logs key
        ({"activity_logs": {"some": "data"}, "other_key": "value"}, {"other_key": "value"}, True),
        # Test case 2: Empty state
        ({}, {}, False),
        # Test case 3: State without activity_logs
        ({"key1": "value1", "key2": "value2"}, {"key1": "value1", "key2": "value2"}, False),
        # Test case 4: State with activity_logs as None
        ({"activity_logs": None, "other_key": "value"}, {"other_key": "value"}, True),
    ],
)
def test_monday_state_migration(input_state, expected_state, expected_should_migrate):
    """Test both migrate and should_migrate methods of MondayStateMigration."""
    migration = MondayStateMigration()

    # Test should_migrate
    should_migrate_result = migration.should_migrate(input_state)
    assert (
        should_migrate_result == expected_should_migrate
    ), f"should_migrate failed: expected {expected_should_migrate}, got {should_migrate_result}"

    if should_migrate_result:
        # Test migrate
        result = migration.migrate(input_state)
        assert result == expected_state, f"migrate failed: expected {expected_state}, got {result}"


def _create_response(content: Any) -> Response:
    response = Response()
    response._content = json.dumps(content).encode("utf-8")
    return response


def test_null_records(caplog):
    extractor = MondayIncrementalItemsExtractor(
        field_path=["data", "boards", "*"],
        config={},
        parameters={},
    )
    content = {
        "data": {
            "boards": [
                {"board_kind": "private", "id": "1234561", "updated_at": "2023-08-15T10:30:49Z"},
                {"board_kind": "private", "id": "1234562", "updated_at": "2023-08-15T10:30:50Z"},
                {"board_kind": "private", "id": "1234563", "updated_at": "2023-08-15T10:30:51Z"},
                {"board_kind": "private", "id": "1234564", "updated_at": "2023-08-15T10:30:52Z"},
                {"board_kind": "private", "id": "1234565", "updated_at": "2023-08-15T10:30:43Z"},
                {"board_kind": "private", "id": "1234566", "updated_at": "2023-08-15T10:30:54Z"},
                None,
                None,
            ]
        },
        "errors": [{"message": "Cannot return null for non-nullable field Board.creator"}],
        "account_id": 123456,
    }
    response = _create_response(content)
    records = list(extractor.extract_records(response))
    warning_message = "Record with null value received; errors: [{'message': 'Cannot return null for non-nullable field Board.creator'}]"
    assert warning_message in caplog.messages
    expected_records = [
        {"board_kind": "private", "id": "1234561", "updated_at": "2023-08-15T10:30:49Z"},
        {"board_kind": "private", "id": "1234562", "updated_at": "2023-08-15T10:30:50Z"},
        {"board_kind": "private", "id": "1234563", "updated_at": "2023-08-15T10:30:51Z"},
        {"board_kind": "private", "id": "1234564", "updated_at": "2023-08-15T10:30:52Z"},
        {"board_kind": "private", "id": "1234565", "updated_at": "2023-08-15T10:30:43Z"},
        {"board_kind": "private", "id": "1234566", "updated_at": "2023-08-15T10:30:54Z"},
    ]
    assert records == expected_records
