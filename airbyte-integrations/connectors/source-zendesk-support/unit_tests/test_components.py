# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import logging
from datetime import datetime
from unittest.mock import MagicMock

import freezegun
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


@pytest.mark.parametrize(
    "stream_state, expected",
    [
        # The flat export cursor of 5.x.
        ({"time": "1780000000"}, True),
        ({"time": 1780000000}, True),
        ({"time": "2026-05-28T00:00:00Z"}, True),
        ({}, False),
        (None, False),
        # Already on the 6.0.0 shape, in either of the forms the CDK accepts.
        ({"_ab_updated_at": "1780000000", "parent_state": {"tickets": {"updated_at": "1780000000"}}}, False),
        ({"use_global_cursor": True, "state": {"_ab_updated_at": "1780000000"}, "parent_state": {}}, False),
        ({"time": "1780000000", "parent_state": {"tickets": {"updated_at": "1780000000"}}}, False),
    ],
)
def test_ticket_metric_events_state_migration_should_migrate(stream_state, expected, components_module):
    migration = components_module.TicketMetricEventsStateMigration()
    assert migration.should_migrate(stream_state) is expected


def _both_parents(updated_at: str) -> dict:
    return {"tickets": {"updated_at": updated_at}, "closed_tickets_search": {"updated_at": updated_at}}


@freezegun.freeze_time("2026-06-01T00:00:00Z")
@pytest.mark.parametrize(
    "stream_state, expected",
    [
        # Rewound by one hour and used for the global cursor and for both parent cursors.
        ({"time": "1780000000"}, {"_ab_updated_at": "1779996400", "parent_state": _both_parents("1779996400")}),
        ({"time": 1780000000}, {"_ab_updated_at": "1779996400", "parent_state": _both_parents("1779996400")}),
        # An ISO-8601 value, as older versions wrote it, is parsed first.
        ({"time": "2026-05-28T00:00:00Z"}, {"_ab_updated_at": "1779922800", "parent_state": _both_parents("1779922800")}),
        # The export dated SLA `breach` events with the future breach moment: a value past the migration
        # time (2026-06-01T00:00:00Z = 1780272000) is clamped to it before the rewind.
        ({"time": "1790000000"}, {"_ab_updated_at": "1780268400", "parent_state": _both_parents("1780268400")}),
        # Never rewinds below the epoch.
        ({"time": "100"}, {"_ab_updated_at": "0", "parent_state": _both_parents("0")}),
        # An unparsable cursor drops the state so the next sync starts from `start_date`.
        ({"time": "not-a-timestamp"}, {}),
        ({"time": None}, {}),
    ],
)
def test_ticket_metric_events_state_migration_migrate(stream_state, expected, components_module):
    migration = components_module.TicketMetricEventsStateMigration()
    assert migration.migrate(stream_state) == expected


@pytest.mark.parametrize(
    "stream_state, expected",
    [
        # The global cursor of a per-ticket substream, handed to the parent when `parent_state` predates it.
        ({"_ab_updated_at": "1780000000"}, True),
        ({"timestamp": "1780000000"}, True),
        ({"created_at": "1780000000"}, True),
        ({"generated_timestamp": "1780000000"}, True),
        # Already keyed on the parent's cursor.
        ({"updated_at": "1780000000"}, False),
        ({}, False),
        (None, False),
    ],
)
def test_closed_tickets_search_state_migration_should_migrate(stream_state, expected, components_module):
    migration = components_module.ClosedTicketsSearchStateMigration()
    assert migration.should_migrate(stream_state) is expected


def _response_with_json(body):
    response = MagicMock()
    response.json.return_value = body
    return response


def test_ticket_metric_sets_extractor_stamps_each_metric_set_with_its_tickets_updated_at(components_module):
    body = {
        "tickets": [
            # `generated_timestamp` is bumped by system-only updates and can be later than `updated_at`;
            # the cursor follows `updated_at`, the field the list is sorted and filtered on.
            {"id": 1, "status": "closed", "updated_at": "2023-05-26T23:02:01Z", "generated_timestamp": 1685142181},
            {"id": 191, "status": "open", "updated_at": "2026-09-28T00:59:20Z", "generated_timestamp": 1790557220},
        ],
        "metric_sets": [
            {"id": 361110475196, "ticket_id": 1, "updated_at": "2023-05-26T23:02:00Z"},
            {"id": 15692756017295, "ticket_id": 191, "updated_at": "2026-09-28T00:58:53Z"},
        ],
    }

    records = components_module.ZendeskSupportTicketMetricSetsExtractor().extract_records(_response_with_json(body))

    # The ticket's status is not looked at: every metric set on the page is emitted.
    assert [(record["id"], record["_ab_updated_at"]) for record in records] == [
        (361110475196, 1685142121),
        (15692756017295, 1790557160),
    ]
    assert records[0]["updated_at"] == "2023-05-26T23:02:00Z"
    assert "generated_timestamp" not in records[0]


def test_ticket_metric_sets_extractor_joins_by_ticket_id_not_by_position(components_module):
    body = {
        "tickets": [
            {"id": 10, "updated_at": "1970-01-01T00:01:40Z"},
            {"id": 20, "updated_at": "1970-01-01T00:03:20Z"},
        ],
        "metric_sets": [
            {"id": 2000, "ticket_id": 20, "updated_at": "2024-01-01T00:00:00Z"},
            {"id": 1000, "ticket_id": 10, "updated_at": "2024-01-01T00:00:00Z"},
        ],
    }

    records = components_module.ZendeskSupportTicketMetricSetsExtractor().extract_records(_response_with_json(body))

    assert [(record["ticket_id"], record["_ab_updated_at"]) for record in records] == [(20, 200), (10, 100)]


def test_ticket_metric_sets_extractor_falls_back_to_updated_at_when_the_ticket_is_not_on_the_page(components_module):
    body = {"tickets": [], "metric_sets": [{"id": 7, "ticket_id": 99, "updated_at": "2024-01-01T00:00:00Z"}]}

    records = components_module.ZendeskSupportTicketMetricSetsExtractor().extract_records(_response_with_json(body))

    assert records == [{"id": 7, "ticket_id": 99, "updated_at": "2024-01-01T00:00:00Z", "_ab_updated_at": 1704067200}]


@pytest.mark.parametrize(
    "body",
    [
        pytest.param({"tickets": [{"id": 1, "updated_at": "2026-01-01T00:00:00Z"}]}, id="no_metric_sets_key"),
        pytest.param({"tickets": [], "metric_sets": None}, id="null_metric_sets"),
        pytest.param({}, id="empty_body"),
        pytest.param([], id="list_body"),
    ],
)
def test_ticket_metric_sets_extractor_returns_nothing_without_metric_sets(body, components_module):
    assert components_module.ZendeskSupportTicketMetricSetsExtractor().extract_records(_response_with_json(body)) == []


def test_ticket_metric_sets_extractor_warns_when_a_ticket_page_has_no_side_load(caplog, components_module):
    body = {"tickets": [{"id": 1, "updated_at": "2026-01-01T00:00:00Z"}, {"id": 2, "updated_at": "2026-01-01T00:00:00Z"}]}

    with caplog.at_level(logging.WARNING, logger="airbyte"):
        records = components_module.ZendeskSupportTicketMetricSetsExtractor().extract_records(_response_with_json(body))

    assert records == []
    assert [r.message for r in caplog.records if r.levelno == logging.WARNING] == [
        "The ticket list page carries no `metric_sets` side-load although it lists 2 tickets; `ticket_metrics` emits nothing for this page."
    ]


@pytest.mark.parametrize(
    "body",
    [
        pytest.param({"tickets": [], "metric_sets": []}, id="empty_page"),
        pytest.param({"tickets": [{"id": 1, "updated_at": "2026-01-01T00:00:00Z"}], "metric_sets": []}, id="side_load_present_but_empty"),
    ],
)
def test_ticket_metric_sets_extractor_does_not_warn_when_the_side_load_is_present(body, caplog, components_module):
    with caplog.at_level(logging.WARNING, logger="airbyte"):
        assert components_module.ZendeskSupportTicketMetricSetsExtractor().extract_records(_response_with_json(body)) == []

    assert [r for r in caplog.records if r.levelno == logging.WARNING] == []


def test_ticket_metric_sets_extractor_returns_nothing_on_non_json_body(components_module):
    response = MagicMock()
    response.json.side_effect = requests.exceptions.JSONDecodeError("Expecting value", "", 0)

    assert components_module.ZendeskSupportTicketMetricSetsExtractor().extract_records(response) == []


# State shapes written by the `ticket_metrics` StateDelegatingStream up to 6.0.0. The incremental path was a
# per-ticket substream of `tickets`, so its state is the ConcurrentPerPartitionCursor shape; 5.x saved the
# parent cursor as `generated_timestamp`, 6.0.0 as `updated_at`.
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
_6_0_0_STATE = {**_PER_PARTITION_STATE, "parent_state": {"tickets": {"updated_at": "1760100000"}}}


@pytest.mark.parametrize(
    "stream_state, expected",
    [
        pytest.param({}, False, id="no_state"),
        pytest.param({"_ab_updated_at": "1760000000"}, False, id="already_new_shape_string"),
        pytest.param({"_ab_updated_at": 1760000000}, False, id="already_new_shape_int_from_full_refresh_path"),
        pytest.param(_PER_PARTITION_STATE, True, id="per_partition"),
        pytest.param(_GLOBAL_CURSOR_STATE, True, id="global_cursor"),
        pytest.param(_6_0_0_STATE, True, id="6_0_0_per_partition"),
        pytest.param({"generated_timestamp": 1700000000}, True, id="pre_4_3_0_cursor"),
        pytest.param({"__ab_no_cursor_state_message": True}, True, id="full_refresh_marker"),
    ],
)
def test_ticket_metrics_state_migration_should_migrate(stream_state, expected, components_module):
    assert components_module.TicketMetricsStateMigration().should_migrate(stream_state) is expected


@pytest.mark.parametrize(
    "stream_state, expected",
    [
        # Re-keyed onto `updated_at` and rewound by one hour, whatever the child's cursor field was.
        ({"_ab_updated_at": "1780000000"}, {"updated_at": "1779996400"}),
        ({"timestamp": 1780000000}, {"updated_at": "1779996400"}),
        ({"created_at": "2026-05-28T00:00:00Z"}, {"updated_at": "1779922800"}),
        ({"generated_timestamp": "1780000000"}, {"updated_at": "1779996400"}),
        # Never rewinds below the epoch.
        ({"_ab_updated_at": "100"}, {"updated_at": "0"}),
        # Anything but a single scalar cursor value drops the cursor: the parent walks from `start_date`.
        ({"_ab_updated_at": "not-a-timestamp"}, {}),
        ({"_ab_updated_at": None}, {}),
        ({"_ab_updated_at": "1780000000", "lookback_window": 0}, {}),
        ({"states": [{"partition": {"ticket_id": 1}, "cursor": {"_ab_updated_at": "1780000000"}}]}, {}),
    ],
)
def test_closed_tickets_search_state_migration_migrate(stream_state, expected, components_module):
    migration = components_module.ClosedTicketsSearchStateMigration()
    assert migration.migrate(stream_state) == expected


@pytest.mark.parametrize(
    "stream_state, expected",
    [
        # A 5.x parent cursor (`generated_timestamp`) gets the one-hour rewind `TicketsStateMigration` gives it.
        pytest.param(_PER_PARTITION_STATE, {"_ab_updated_at": "1760096400"}, id="per_partition_resumes_from_parent_cursor_rewound"),
        pytest.param(_GLOBAL_CURSOR_STATE, {"_ab_updated_at": "1760096400"}, id="global_cursor_resumes_from_parent_cursor_rewound"),
        # A 6.0.0 parent cursor (`updated_at`) is already on the list's sort key and is used as is.
        pytest.param(_6_0_0_STATE, {"_ab_updated_at": "1760100000"}, id="6_0_0_resumes_from_parent_updated_at"),
        pytest.param(
            # An intermediate checkpoint: the parent cursor has advanced, the global cursor still holds the
            # previous sync's value.
            {**_6_0_0_STATE, "state": {"_ab_updated_at": "1750000000"}},
            {"_ab_updated_at": "1760100000"},
            id="intermediate_checkpoint_uses_parent_cursor",
        ),
        pytest.param(
            {**_PER_PARTITION_STATE, "parent_state": {"tickets": {"generated_timestamp": 1760100000}}},
            {"_ab_updated_at": "1760096400"},
            id="int_parent_cursor",
        ),
        # Without a parent cursor the saved `_ab_updated_at` is a ticket's `generated_timestamp` (what the
        # per-ticket path stamped), so it gets the same one-hour rewind.
        pytest.param(
            {**_PER_PARTITION_STATE, "parent_state": {"tickets": {"generated_timestamp": "not a timestamp"}}},
            {"_ab_updated_at": "1759996400"},
            id="unparsable_parent_cursor_falls_back_to_global_cursor_rewound",
        ),
        pytest.param(
            {key: value for key, value in _PER_PARTITION_STATE.items() if key != "parent_state"},
            {"_ab_updated_at": "1759996400"},
            id="no_parent_state_falls_back_to_global_cursor_rewound",
        ),
        pytest.param(
            {**_PER_PARTITION_STATE, "parent_state": {"tickets": {}}},
            {"_ab_updated_at": "1759996400"},
            id="empty_parent_state_falls_back_to_global_cursor_rewound",
        ),
        pytest.param(
            {"_ab_updated_at": "1760000000", "parent_state": {}},
            {"_ab_updated_at": "1759996400"},
            id="flat_cursor_next_to_other_keys_rewound",
        ),
        pytest.param(
            {"use_global_cursor": False, "states": [], "parent_state": {"tickets": {"generated_timestamp": "1760100000"}}},
            {"_ab_updated_at": "1760096400"},
            id="first_sync_interrupted_parent_only",
        ),
        pytest.param({"generated_timestamp": 1700000000}, {"_ab_updated_at": "1699996400"}, id="pre_4_3_0_cursor_rewound"),
        pytest.param({"generated_timestamp": 100}, {"_ab_updated_at": "0"}, id="rewind_floors_at_epoch"),
        pytest.param({"__ab_no_cursor_state_message": True}, {}, id="full_refresh_marker_restarts_from_start_date"),
        pytest.param({"use_global_cursor": False, "states": []}, {}, id="no_cursor_restarts_from_start_date"),
    ],
)
def test_ticket_metrics_state_migration_migrate(stream_state, expected, components_module):
    assert components_module.TicketMetricsStateMigration().migrate(stream_state) == expected


@pytest.mark.parametrize("stream_state", [_PER_PARTITION_STATE, _GLOBAL_CURSOR_STATE, _6_0_0_STATE])
def test_ticket_metrics_state_migration_is_idempotent(stream_state, components_module):
    migration = components_module.TicketMetricsStateMigration()
    migrated = migration.migrate(stream_state)

    assert not migration.should_migrate(migrated)
    assert migration.migrate(migrated) == migrated
