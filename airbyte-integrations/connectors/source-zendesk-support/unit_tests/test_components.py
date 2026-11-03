# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime
from unittest.mock import MagicMock

import pytest
import requests


@pytest.mark.parametrize(
    "response_data, expected_comments",
    [
        pytest.param({"some_other_data": [{}]}, [], id="no audits key"),
        pytest.param({"audits": []}, [], id="no audits"),
        pytest.param(
            {"audits": [{"id": 1, "ticket_id": 456, "created_at": "2022-01-01T00:00:00Z", "via": {"channel": "web"}}]}, [], id="no events"
        ),
        pytest.param(
            {
                "audits": [
                    {
                        "id": 1,
                        "ticket_id": 456,
                        "created_at": "2022-01-01T00:00:00Z",
                        "via": {"channel": "web", "source": {"from": {}, "to": {}, "rel": None}},
                        "events": [
                            {"id": 10, "type": "Create", "field_name": "subject", "value": "Help"},
                            {"id": 11, "type": "Comment", "body": "Hello", "public": True, "author_id": 7, "audit_id": 1},
                            {"id": 12, "type": "VoiceComment", "body": "Voicemail"},
                        ],
                    }
                ]
            },
            [
                {
                    "id": 11,
                    "type": "Comment",
                    "body": "Hello",
                    "public": True,
                    "author_id": 7,
                    "audit_id": 1,
                    "ticket_id": 456,
                    "created_at": "2022-01-01T00:00:00Z",
                    "timestamp": 1640995200,
                    "via": {"channel": "web", "source": {"from": {}, "to": {}, "rel": None}},
                    "via_reference_id": None,
                    "event_type": "Comment",
                }
            ],
            id="only Comment events, with the audit's ticket_id, created_at, timestamp and via",
        ),
        pytest.param(
            {
                "audits": [
                    {"id": 1, "ticket_id": 456, "created_at": None, "via": "incorrect_format", "events": [{"id": 11, "type": "Comment"}]}
                ]
            },
            [
                {
                    "id": 11,
                    "type": "Comment",
                    "ticket_id": 456,
                    "created_at": None,
                    "timestamp": None,
                    "via": None,
                    "via_reference_id": None,
                    "event_type": "Comment",
                }
            ],
            id="non-object via and missing created_at become null",
        ),
    ],
)
def test_audit_comments_extractor(response_data, expected_comments, components_module):
    extractor = components_module.ZendeskSupportAuditCommentsExtractor()
    response = MagicMock(spec=requests.Response)
    response.json.return_value = response_data

    comments = extractor.extract_records(response)

    assert comments == expected_comments


def test_audit_comments_extractor_given_non_json_body_then_return_nothing(components_module):
    extractor = components_module.ZendeskSupportAuditCommentsExtractor()
    response = MagicMock(spec=requests.Response)
    response.json.side_effect = requests.exceptions.JSONDecodeError("Expecting value", "<html>", 0)

    assert extractor.extract_records(response) == []


@pytest.mark.parametrize(
    "response_data, expected_records",
    [
        # Test case with both conditions_all and conditions_any properly filled
        (
            {"definitions": {"conditions_all": [{"id": 1}], "conditions_any": [{"id": 2}]}},
            [{"id": 1, "condition": "all"}, {"id": 2, "condition": "any"}],
        ),
        # Test case where conditions_all is empty
        ({"definitions": {"conditions_any": [{"id": 2}], "conditions_all": []}}, [{"id": 2, "condition": "any"}]),
        # Test case where conditions_any is empty
        ({"definitions": {"conditions_all": [{"id": 1}], "conditions_any": []}}, [{"id": 1, "condition": "all"}]),
        # Test case where both conditions are empty
        ({"definitions": {"conditions_all": [], "conditions_any": []}}, []),
        # Test case with malformed JSON (simulate JSONDecodeError)
        (None, []),  # This will be used to mock an exception in the response.json() call
    ],
)
def test_attribute_definitions_extractor(response_data, expected_records, components_module):
    # Create an instance of the extractor
    extractor = components_module.ZendeskSupportAttributeDefinitionsExtractor()

    # Mock the response from requests
    response = MagicMock(spec=requests.Response)
    if response_data is None:
        response.json.side_effect = requests.exceptions.JSONDecodeError("Expecting value", "", 0)
    else:
        response.json.return_value = response_data

    # Invoke the extract_records method
    records = extractor.extract_records(response)

    # Assert that the returned records match the expected records
    assert records == expected_records, f"Expected records to be {expected_records}, but got {records}"


@pytest.mark.parametrize(
    "stream_state, expected",
    [
        ({"generated_timestamp": "1780000000"}, True),
        ({"generated_timestamp": 1780000000}, True),
        # Parent state of a per-ticket substream after a 5.x sync.
        ({"generated_timestamp": "1780000000", "extra": 1}, True),
        ({}, False),
        (None, False),
        ({"updated_at": "1780000000"}, False),
        # Already migrated, or written by 5.2.x: never rewound again.
        ({"updated_at": "1780000000", "generated_timestamp": "1780000000"}, False),
    ],
)
def test_tickets_state_migration_should_migrate(stream_state, expected, components_module):
    migration = components_module.TicketsStateMigration()
    assert migration.should_migrate(stream_state) is expected


@pytest.mark.parametrize(
    "stream_state, expected",
    [
        # Rewound by one hour onto the new cursor field, as a "%s" string like the cursor writes it.
        ({"generated_timestamp": "1780000000"}, {"updated_at": "1779996400"}),
        ({"generated_timestamp": 1780000000}, {"updated_at": "1779996400"}),
        # Never rewinds below the epoch.
        ({"generated_timestamp": "100"}, {"updated_at": "0"}),
        # An unparsable cursor drops the state so the next sync starts from `start_date`.
        ({"generated_timestamp": "not-a-timestamp"}, {}),
        ({"generated_timestamp": None}, {}),
    ],
)
def test_tickets_state_migration_migrate(stream_state, expected, components_module):
    migration = components_module.TicketsStateMigration()
    assert migration.migrate(stream_state) == expected
