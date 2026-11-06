#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
import copy
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
_LAST_EDITED_TIME = "2023-01-01T00:00:00.000Z"


def _legacy_notion_user_transformation(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reference implementation of the NotionUserTransformation class removed from components.py.
    Kept here to prove that the declarative AddFields replacement produces identical record output.
    """
    owner = record.get("bot", {}).get("owner")
    if owner:
        owner_type = owner.get("type")
        owner_info = owner.get(owner_type)
        if owner_type and owner_info:
            record["bot"]["owner"]["info"] = owner_info
            del record["bot"]["owner"][owner_type]
    return record


def _legacy_notion_properties_transformation(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reference implementation of the NotionPropertiesTransformation class removed from components.py.
    Kept here to prove that the declarative AddFields replacement produces identical record output.
    """
    properties = record.get("properties", {})
    transformed_properties = [{"name": name, "value": value} for name, value in properties.items()]
    record["properties"] = transformed_properties
    return record


def _read_records(
    requests_mock,
    stream_name: str,
    records: List[Dict[str, Any]],
    sync_mode: str = "full_refresh",
    state: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    response_body = {"object": "list", "results": records, "next_cursor": None, "has_more": False}
    if stream_name == "users":
        requests_mock.register_uri("GET", "https://api.notion.com/v1/users", [{"json": response_body}])
    else:
        requests_mock.register_uri("POST", "https://api.notion.com/v1/search", [{"json": response_body}])
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {
                        "name": stream_name,
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh", "incremental"],
                    },
                    "sync_mode": sync_mode,
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    state = state if state is not None else StateBuilder().with_stream_state(stream_name, {}).build()
    source = get_source(_CONFIG, state)
    output = read(source, config=_CONFIG, catalog=catalog, state=state)
    return [record.record.data for record in output.records]


_USER_CASES = [
    {"id": "p", "type": "person", "person": {"email": "a"}},
    {"id": "b0", "type": "bot", "bot": {}},
    {"id": "b1", "type": "bot", "bot": {"owner": None}},
    {"id": "b2", "type": "bot", "bot": {"owner": {"type": "workspace", "workspace": True}, "workspace_name": "w"}},
    {
        "id": "b3",
        "type": "bot",
        "bot": {
            "owner": {
                "type": "user",
                "user": {
                    "object": "user",
                    "id": "x",
                    "name": 'It\'s "q" {{ x }}',
                    "avatar_url": None,
                    "type": "person",
                    "person": {"email": "e"},
                },
            }
        },
    },
    {"id": "b4", "type": "bot", "bot": {"owner": {"type": "user", "user": {}}}},
    {"id": "b5", "type": "bot", "bot": {"owner": {"type": "workspace", "workspace": False}}},
    {"id": "b6", "type": "bot", "bot": {"owner": {"type": None, "workspace": True}}},
    {"id": "b7", "type": "bot", "bot": {"owner": {"workspace": True}}},
    {"id": "b8", "type": "bot", "bot": {"owner": {"type": "user", "user": {"id": "u"}, "info": "old", "extra": 1}}},
    {"id": "b9", "type": "bot", "bot": {"owner": {"type": "other", "other": [1, 2.5, 10**20, "\\n\n"]}}},
    {"id": "b11", "type": "bot"},
    {"id": "b12", "type": "bot", "bot": {"owner": {}}},
]


@pytest.mark.parametrize("record", _USER_CASES, ids=lambda r: r["id"])
def test_users_stream_transformation_matches_legacy(requests_mock, record):
    expected = _legacy_notion_user_transformation(copy.deepcopy(record))
    output_records = _read_records(requests_mock, "users", [record])
    assert len(output_records) == 1
    out = output_records[0]
    assert out == expected
    if isinstance(out.get("bot"), dict) and isinstance(out["bot"].get("owner"), dict):
        assert list(out["bot"]["owner"]) == list(expected["bot"]["owner"])


_DUE_DATE_STATUS_RECORD = {
    "id": "due-date-status",
    "properties": {
        "Due date": {"id": "M%3BBw", "type": "date", "date": {"start": "2023-02-23", "end": None, "time_zone": None}},
        "Status": {
            "id": "Z%3ClH",
            "type": "status",
            "status": {"id": "86ddb6ec-0627-47f8-800d-b65afd28be13", "name": "Not started", "color": "default"},
        },
    },
}

_PROPERTIES_CASES = [
    {"id": "1", "properties": {}},
    {"id": "2"},
    {
        "id": "4",
        "properties": {
            "Name": {
                "id": "title",
                "type": "title",
                "title": [{"plain_text": 'It\'s "x" {{ y }} {% raw %}\\ \n ü'}],
            },
            "Done": {"type": "checkbox", "checkbox": False},
            "N": {"type": "number", "number": 1.5},
            "Big": {"number": 10**20},
            "Nil": None,
        },
    },
    _DUE_DATE_STATUS_RECORD,
]


@pytest.mark.parametrize("stream_name", ["pages", "data_sources"])
@pytest.mark.parametrize("record", _PROPERTIES_CASES, ids=lambda r: r["id"])
def test_properties_transformation_matches_legacy(requests_mock, stream_name, record):
    record = dict(record, last_edited_time=_LAST_EDITED_TIME)
    expected = _legacy_notion_properties_transformation(copy.deepcopy(record))
    output_records = _read_records(requests_mock, stream_name, [record])
    assert len(output_records) == 1
    assert output_records[0] == expected


def test_users_stream_transformation_literal(requests_mock):
    input_record = {
        "object": "user",
        "id": "123",
        "name": "Airbyte",
        "avatar_url": "some url",
        "type": "bot",
        "bot": {
            "owner": {
                "type": "user",
                "user": {
                    "object": "user",
                    "id": "id",
                    "name": "Test User",
                    "avatar_url": None,
                    "type": "person",
                    "person": {"email": "email"},
                },
            },
            "workspace_name": "test",
        },
    }
    expected_record = {
        "object": "user",
        "id": "123",
        "name": "Airbyte",
        "avatar_url": "some url",
        "type": "bot",
        "bot": {
            "owner": {
                "type": "user",
                "info": {
                    "object": "user",
                    "id": "id",
                    "name": "Test User",
                    "avatar_url": None,
                    "type": "person",
                    "person": {"email": "email"},
                },
            },
            "workspace_name": "test",
        },
    }
    output_records = _read_records(requests_mock, "users", [input_record])
    assert output_records == [expected_record]


def test_properties_transformation_literal(requests_mock):
    input_record = dict(_DUE_DATE_STATUS_RECORD, last_edited_time=_LAST_EDITED_TIME)
    expected_record = {
        "id": "due-date-status",
        "last_edited_time": _LAST_EDITED_TIME,
        "properties": [
            {
                "name": "Due date",
                "value": {"id": "M%3BBw", "type": "date", "date": {"start": "2023-02-23", "end": None, "time_zone": None}},
            },
            {
                "name": "Status",
                "value": {
                    "id": "Z%3ClH",
                    "type": "status",
                    "status": {"id": "86ddb6ec-0627-47f8-800d-b65afd28be13", "name": "Not started", "color": "default"},
                },
            },
        ],
    }
    output_records = _read_records(requests_mock, "pages", [input_record])
    assert output_records == [expected_record]


@pytest.mark.parametrize(
    "owner",
    [
        {"type": "user", "user": {}},
        {"type": "workspace", "workspace": False},
    ],
    ids=["empty-user", "false-workspace"],
)
def test_users_stream_transformation_falsy_owner_values_preserved(requests_mock, owner):
    input_record = {"id": "bot-1", "type": "bot", "bot": {"owner": owner}}
    output_records = _read_records(requests_mock, "users", [input_record])
    assert len(output_records) == 1
    assert output_records[0] == input_record
    assert "info" not in output_records[0]["bot"]["owner"]


def test_users_stream_transformation_person_without_bot(requests_mock):
    input_record = {"object": "user", "id": "p1", "type": "person", "person": {"email": "a@b.c"}}
    output_records = _read_records(requests_mock, "users", [input_record])
    assert output_records == [input_record]


def test_no_custom_transformations_referenced(components_module):
    manifest_text = (Path(__file__).parent.parent / "manifest.yaml").read_text()
    for class_name in ("NotionUserTransformation", "NotionPropertiesTransformation", "CustomTransformation"):
        assert class_name not in manifest_text
    for class_name in ("NotionUserTransformation", "NotionPropertiesTransformation"):
        assert not hasattr(components_module, class_name)


def test_pages_incremental_state_filters_and_transforms(requests_mock):
    records = [
        {"id": "old", "last_edited_time": "2023-01-01T00:00:00.000Z", "properties": {"P": {"type": "number", "number": 1}}},
        {"id": "new", "last_edited_time": "2023-07-01T00:00:00.000Z", "properties": {"P": {"type": "number", "number": 2}}},
    ]
    state = StateBuilder().with_stream_state("pages", {"last_edited_time": "2023-06-01T00:00:00.000Z"}).build()
    output_records = _read_records(requests_mock, "pages", records, sync_mode="incremental", state=state)
    assert output_records == [
        {
            "id": "new",
            "last_edited_time": "2023-07-01T00:00:00.000Z",
            "properties": [{"name": "P", "value": {"type": "number", "number": 2}}],
        }
    ]
