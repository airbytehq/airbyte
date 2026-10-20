# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
import requests


@pytest.mark.parametrize(
    "response_data, expected_events",
    [
        # Test case with no ticket_events in response
        ({"some_other_data": [{}]}, []),
        # Test case with empty ticket_events
        ({"ticket_events": []}, []),
        # Test case with ticket_events but no child_events
        ({"ticket_events": [{"via_reference_id": 123, "ticket_id": 456, "timestamp": "2022-01-01T00:00:00Z"}]}, []),
        # Test case with valid child_events and Comment event_type
        (
            {
                "ticket_events": [
                    {
                        "via_reference_id": 123,
                        "ticket_id": 456,
                        "timestamp": "2022-01-01T00:00:00Z",
                        "child_events": [{"event_type": "Comment", "via_reference_id": "unused", "via": {"some": "data"}}],
                    }
                ]
            },
            [
                {
                    "event_type": "Comment",
                    "via_reference_id": 123,
                    "ticket_id": 456,
                    "timestamp": "2022-01-01T00:00:00Z",
                    "via": {"some": "data"},
                }
            ],
        ),
        # Test case with an invalid 'via' property format
        (
            {
                "ticket_events": [
                    {
                        "via_reference_id": 123,
                        "ticket_id": 456,
                        "timestamp": "2022-01-01T00:00:00Z",
                        "child_events": [{"event_type": "Comment", "via_reference_id": "unused", "via": "incorrect_format"}],
                    }
                ]
            },
            [{"event_type": "Comment", "via_reference_id": 123, "ticket_id": 456, "timestamp": "2022-01-01T00:00:00Z", "via": None}],
        ),
    ],
)
def test_extraсtor_events(response_data, expected_events, components_module):
    # Create an instance of the extractor
    extractor = components_module.ZendeskSupportExtractorEvents()

    # Mock the response from requests
    response = MagicMock(spec=requests.Response)
    response.json.return_value = response_data

    # Invoke the extract_records method
    events = extractor.extract_records(response)

    # Assert that the returned events match the expected events
    assert events == expected_events, f"Expected events to be {expected_events}, but got {events}"


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


def test_backfill_floor_precedes_the_5_2_0_regression(components_module):
    """The floor is a bare epoch int, so pin it to the date it is supposed to mean.

    v5.2.0 -- the release that switched `tickets` to the `updated_at` cursor -- merged on 2026-03-12, so the
    floor has to sit before that for the one-time backfill to cover the whole regression window.
    """
    floor = components_module.TicketsStateMigration.BACKFILL_FLOOR

    assert datetime.fromtimestamp(floor, timezone.utc) == datetime(2026, 3, 1, tzinfo=timezone.utc)
    assert floor < datetime(2026, 3, 12, tzinfo=timezone.utc).timestamp()


@pytest.mark.parametrize(
    "stream_state, expected",
    [
        ({"updated_at": "1780000000"}, True),
        ({}, False),
        ({"generated_timestamp": 123}, False),
    ],
)
def test_tickets_state_migration_should_migrate(stream_state, expected, components_module):
    migration = components_module.TicketsStateMigration()
    assert migration.should_migrate(stream_state) is expected


@pytest.mark.parametrize(
    "stream_state, expected",
    [
        # Above the floor -> clamped down to the floor.
        ({"updated_at": "1780000000"}, "floor"),
        # Below the floor -> left unchanged.
        ({"updated_at": "1000000000"}, {"generated_timestamp": 1000000000}),
    ],
)
def test_tickets_state_migration_migrate(stream_state, expected, components_module):
    migration = components_module.TicketsStateMigration()
    if expected == "floor":
        expected = {"generated_timestamp": migration.BACKFILL_FLOOR}
    assert migration.migrate(stream_state) == expected


def _response_with_json(body):
    response = MagicMock()
    response.json.return_value = body
    return response


def test_ticket_metric_sets_extractor_stamps_each_metric_set_with_its_tickets_generated_timestamp(components_module):
    body = {
        "tickets": [
            {"id": 1, "status": "closed", "generated_timestamp": 1685142121},
            {"id": 191, "status": "deleted", "generated_timestamp": 1790557160},
        ],
        "metric_sets": [
            {"id": 361110475196, "ticket_id": 1, "updated_at": "2023-05-26T23:02:00Z"},
            {"id": 15692756017295, "ticket_id": 191, "updated_at": "2026-09-28T00:58:53Z"},
        ],
    }

    records = components_module.ZendeskSupportTicketMetricSetsExtractor().extract_records(_response_with_json(body))

    # Archived (closed) and deleted tickets are emitted like any other: the per-ticket endpoint
    # returns their metrics too.
    assert [(record["id"], record["_ab_updated_at"]) for record in records] == [
        (361110475196, 1685142121),
        (15692756017295, 1790557160),
    ]
    assert "generated_timestamp" not in records[0]


def test_ticket_metric_sets_extractor_falls_back_to_updated_at_when_the_ticket_is_not_on_the_page(components_module):
    body = {"tickets": [], "metric_sets": [{"id": 7, "ticket_id": 99, "updated_at": "2024-01-01T00:00:00Z"}]}

    records = components_module.ZendeskSupportTicketMetricSetsExtractor().extract_records(_response_with_json(body))

    assert records == [{"id": 7, "ticket_id": 99, "updated_at": "2024-01-01T00:00:00Z", "_ab_updated_at": 1704067200}]


@pytest.mark.parametrize(
    "body",
    [
        pytest.param({"tickets": [{"id": 1, "generated_timestamp": 1}]}, id="no_metric_sets_key"),
        pytest.param({"tickets": [], "metric_sets": None}, id="null_metric_sets"),
        pytest.param({}, id="empty_body"),
    ],
)
def test_ticket_metric_sets_extractor_returns_nothing_without_metric_sets(body, components_module):
    assert components_module.ZendeskSupportTicketMetricSetsExtractor().extract_records(_response_with_json(body)) == []


def test_ticket_metric_sets_extractor_returns_nothing_on_non_json_body(components_module):
    response = MagicMock()
    response.json.side_effect = requests.exceptions.JSONDecodeError("Expecting value", "", 0)

    assert components_module.ZendeskSupportTicketMetricSetsExtractor().extract_records(response) == []


# State shapes written by the 5.6.x `ticket_metrics` StateDelegatingStream. The incremental path was a
# per-ticket substream of `tickets`, so its state is the ConcurrentPerPartitionCursor shape.
_PER_PARTITION_STATE = {
    "use_global_cursor": False,
    "lookback_window": 0,
    "state": {"_ab_updated_at": "1760000000"},
    "states": [
        {"partition": {"ticket_id": 35436, "parent_slice": {}}, "cursor": {"_ab_updated_at": "1760000000"}},
        {"partition": {"ticket_id": 35437, "parent_slice": {}}, "cursor": {"_ab_updated_at": "1759990000"}},
    ],
    "parent_state": {"tickets": {"generated_timestamp": "1760100000"}},
}
# Above 10,000 partitions the cursor switches to a global cursor and drops `states`.
_GLOBAL_CURSOR_STATE = {
    "use_global_cursor": True,
    "lookback_window": 3600,
    "state": {"_ab_updated_at": "1760000000"},
    "parent_state": {"tickets": {"generated_timestamp": "1760100000"}},
}


@pytest.mark.parametrize(
    "stream_state, expected",
    [
        pytest.param({}, False, id="no_state"),
        pytest.param({"_ab_updated_at": "1760000000"}, False, id="already_new_shape_string"),
        pytest.param({"_ab_updated_at": 1760000000}, False, id="already_new_shape_int_from_full_refresh_path"),
        pytest.param(_PER_PARTITION_STATE, True, id="per_partition"),
        pytest.param(_GLOBAL_CURSOR_STATE, True, id="global_cursor"),
        pytest.param({"generated_timestamp": 1700000000}, True, id="pre_4_3_0_cursor"),
        pytest.param({"__ab_no_cursor_state_message": True}, True, id="full_refresh_marker"),
    ],
)
def test_ticket_metrics_state_migration_should_migrate(stream_state, expected, components_module):
    assert components_module.TicketMetricsStateMigration().should_migrate(stream_state) is expected


@pytest.mark.parametrize(
    "stream_state, expected",
    [
        pytest.param(_PER_PARTITION_STATE, {"_ab_updated_at": "1760100000"}, id="per_partition_resumes_from_parent_cursor"),
        pytest.param(_GLOBAL_CURSOR_STATE, {"_ab_updated_at": "1760100000"}, id="global_cursor_resumes_from_parent_cursor"),
        pytest.param(
            # An intermediate checkpoint: the parent cursor has advanced, the global cursor still holds the
            # previous sync's value.
            {**_PER_PARTITION_STATE, "state": {"_ab_updated_at": "1750000000"}},
            {"_ab_updated_at": "1760100000"},
            id="intermediate_checkpoint_uses_parent_cursor",
        ),
        pytest.param(
            {**_PER_PARTITION_STATE, "parent_state": {"tickets": {"generated_timestamp": 1760100000}}},
            {"_ab_updated_at": "1760100000"},
            id="int_parent_cursor",
        ),
        pytest.param(
            {key: value for key, value in _PER_PARTITION_STATE.items() if key != "parent_state"},
            {"_ab_updated_at": "1760000000"},
            id="no_parent_state_falls_back_to_global_cursor",
        ),
        pytest.param(
            {**_PER_PARTITION_STATE, "parent_state": {"tickets": {}}},
            {"_ab_updated_at": "1760000000"},
            id="empty_parent_state_falls_back_to_global_cursor",
        ),
        pytest.param(
            # A parent still on the 5.2.x-5.4.x `updated_at` key gets the same backfill clamp as `tickets`.
            {**_PER_PARTITION_STATE, "parent_state": {"tickets": {"updated_at": "1780000000"}}},
            {"_ab_updated_at": "1772323200"},
            id="legacy_parent_updated_at_is_clamped_to_tickets_backfill_floor",
        ),
        pytest.param(
            {**_PER_PARTITION_STATE, "parent_state": {"tickets": {"updated_at": "1700000000"}}},
            {"_ab_updated_at": "1700000000"},
            id="legacy_parent_updated_at_below_floor_is_kept",
        ),
        pytest.param(
            {"use_global_cursor": False, "states": [], "parent_state": {"tickets": {"generated_timestamp": "1760100000"}}},
            {"_ab_updated_at": "1760100000"},
            id="first_sync_interrupted_parent_only",
        ),
        pytest.param({"generated_timestamp": 1700000000}, {"_ab_updated_at": "1700000000"}, id="pre_4_3_0_cursor"),
        pytest.param({"__ab_no_cursor_state_message": True}, {}, id="full_refresh_marker_restarts_from_start_date"),
        pytest.param({"use_global_cursor": False, "states": []}, {}, id="no_cursor_restarts_from_start_date"),
    ],
)
def test_ticket_metrics_state_migration_migrate(stream_state, expected, components_module):
    assert components_module.TicketMetricsStateMigration().migrate(stream_state) == expected


def test_ticket_metrics_state_migration_is_idempotent(components_module):
    migration = components_module.TicketMetricsStateMigration()
    migrated = migration.migrate(_PER_PARTITION_STATE)

    assert not migration.should_migrate(migrated)
