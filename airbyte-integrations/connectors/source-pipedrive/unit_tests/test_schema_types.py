# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Declared JSON types follow Pipedrive's API reference.

Values in the shape Pipedrive documents must validate against the declared stream schemas, otherwise
typed destinations drop them (lead ids are UUIDs; amounts can be fractional).
"""

from pathlib import Path

import jsonschema
import pytest
import yaml


_SCHEMAS = yaml.safe_load((Path(__file__).parent.parent / "manifest.yaml").read_text())["schemas"]
_LEAD_UUID = "adf21080-0e10-11eb-879b-05d71fb426ec"


@pytest.mark.parametrize(
    "stream, record",
    [
        pytest.param("notes", {"id": 1, "lead_id": _LEAD_UUID}, id="notes_lead_id_is_a_uuid"),
        pytest.param(
            "files",
            {"id": 1, "lead_id": _LEAD_UUID, "cid": "image001.png@01DB2F3A.4B5C6D70", "mail_message_id": "44", "mail_template_id": "7"},
            id="files_ids_are_strings",
        ),
        pytest.param("filters", {"id": 1, "temporary_flag": True}, id="filters_temporary_flag_is_boolean"),
        pytest.param("leads", {"id": _LEAD_UUID, "value": {"amount": 1234.56, "currency": "EUR"}}, id="leads_amount_can_be_fractional"),
        pytest.param(
            "mailThreads",
            {
                "id": 1,
                "archived_flag": None,
                "drafts_parties": None,
                "snippet_sent": None,
                "last_message_received_timestamp": None,
                "parties": {
                    "from": [{"id": 1, "linked_person_id": None, "linked_person_name": None}],
                    "to": [{"id": 2, "linked_person_id": None, "linked_person_name": None}],
                },
            },
            id="mail_threads_nullable_fields_accept_null",
        ),
    ],
)
def test_vendor_shaped_values_validate_against_the_declared_schema(stream, record):
    jsonschema.validate(record, _SCHEMAS[stream])


_TZ = ("date-time", "timestamp_with_timezone")
_NO_TZ = ("date-time", "timestamp_without_timezone")
_DATE = ("date", None)


def _prop(stream, path):
    node = _SCHEMAS[stream]
    for name in path:
        node = node["properties"][name]
    return node


@pytest.mark.parametrize(
    "stream, path, expected",
    [
        *[("projects", [f], _TZ) for f in ("add_time", "update_time", "status_change_time", "archive_time")],
        *[("projects", [f], _DATE) for f in ("start_date", "end_date")],
        *[("tasks", [f], _TZ) for f in ("add_time", "update_time", "marked_as_done_time")],
        *[("tasks", [f], _DATE) for f in ("due_date", "start_date")],
        *[
            ("mailThreads", [f], _TZ)
            for f in (
                "add_time",
                "update_time",
                "first_message_timestamp",
                "last_message_timestamp",
                "last_message_sent_timestamp",
                "last_message_received_timestamp",
            )
        ],
        # The vendor describes YYYY-MM-DD HH:MM:SS, but its example and live values are RFC3339 with Z.
        *[("call_logs", [f], _TZ) for f in ("start_time", "end_time")],
        ("legacy_teams", ["add_time"], _NO_TZ),
        ("deal_flow", ["log_time"], _NO_TZ),
        ("filters", ["last_used_time"], _NO_TZ),
        ("deal_installments", ["billing_date"], _DATE),
        ("goals", ["duration", "start"], _DATE),
        ("goals", ["duration", "end"], _DATE),
        ("leads", ["archive_time"], _TZ),
    ],
)
def test_date_like_fields_declare_their_vendor_shape(stream, path, expected):
    prop = _prop(stream, path)
    assert (prop.get("format"), prop.get("airbyte_type")) == expected


@pytest.mark.parametrize(
    "path",
    [["owner_id"], ["assignee", "id"]],
)
def test_goal_ids_are_integers(path):
    assert "integer" in _prop("goals", path)["type"]


def test_goal_list_ids_are_integers_and_the_target_keeps_fractions():
    params = _prop("goals", ["type", "params"])["properties"]
    assert "integer" in params["pipeline_id"]["items"]["type"]
    assert "integer" in params["activity_type_id"]["items"]["type"]
    # A sum goal's target is a currency amount.
    assert "number" in _prop("goals", ["expected_outcome", "target"])["type"]


@pytest.mark.parametrize(
    "stream, record",
    [
        pytest.param("leads", {"id": _LEAD_UUID, "label_ids": [_LEAD_UUID]}, id="lead_label_ids_are_strings"),
        pytest.param("mailThreads", {"id": 1, "drafts_parties": [{"id": 3, "name": "Jane"}]}, id="drafts_parties_are_objects"),
        pytest.param(
            "deal_fields",
            {"id": 1, "show_in_pipelines": {"show_in_all": False, "pipeline_ids": [1, 2]}},
            id="show_in_pipelines_properties",
        ),
    ],
)
def test_vendor_shaped_collections_validate(stream, record):
    jsonschema.validate(record, _SCHEMAS[stream])


@pytest.mark.parametrize(
    "stream, record",
    [
        pytest.param("leads", {"id": _LEAD_UUID, "label_ids": [1]}, id="lead_label_ids_reject_integers"),
        pytest.param("deal_fields", {"id": 1, "show_in_pipelines": {"pipeline_ids": ["x"]}}, id="pipeline_ids_reject_strings"),
        pytest.param("mailThreads", {"id": 1, "drafts_parties": ["x"]}, id="drafts_parties_reject_strings"),
    ],
)
def test_collection_item_types_are_enforced(stream, record):
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(record, _SCHEMAS[stream])


_STR, _INT = ["null", "string"], ["null", "integer"]


@pytest.mark.parametrize(
    "stream, field, expected_type",
    [
        *[(s, "description", _STR) for s in ("deal_fields", "person_fields", "organization_fields", "activity_fields", "product_fields")],
        *[(s, "group_id", _INT) for s in ("person_fields", "activity_fields", "product_fields")],
        *[(s, "id_suffix", _STR) for s in ("person_fields", "product_fields")],
        ("tasks", "last_updated_by_id", _INT),
        ("tasks", "marked_as_done_by_id", _INT),
        # Pipedrive documents none of these and the test account returns none, so any value must pass.
        *[(s, "restriction_settings", None) for s in ("deal_fields", "person_fields", "organization_fields", "activity_fields")],
        ("deal_fields", "user_restrictions", None),
        ("goals", "seasonality", None),
    ],
)
def test_fields_seen_in_production_are_declared(stream, field, expected_type):
    assert _prop(stream, [field]).get("type") == expected_type
