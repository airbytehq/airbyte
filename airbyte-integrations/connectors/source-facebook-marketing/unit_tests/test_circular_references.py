#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Iterable, Mapping

import pytest
from facebook_business.adobjects.abstractobject import AbstractObject
from source_facebook_marketing.streams.common import sanitize_circular_references


@pytest.mark.parametrize(
    "build_input,expected",
    [
        pytest.param(
            lambda: {"a": 1, "b": "hello", "c": [1, 2, 3]},
            {"a": 1, "b": "hello", "c": [1, 2, 3]},
            id="flat_dict_no_circular_ref",
        ),
        pytest.param(
            lambda: {"a": {"b": {"c": 42}}},
            {"a": {"b": {"c": 42}}},
            id="nested_dict_no_circular_ref",
        ),
        pytest.param(
            lambda: [1, [2, [3]]],
            [1, [2, [3]]],
            id="nested_list_no_circular_ref",
        ),
        pytest.param(
            lambda: 42,
            42,
            id="scalar_int",
        ),
        pytest.param(
            lambda: "hello",
            "hello",
            id="scalar_string",
        ),
        pytest.param(
            lambda: None,
            None,
            id="none_value",
        ),
    ],
)
def test_sanitize_no_circular_references(build_input, expected):
    result = sanitize_circular_references(build_input())
    assert result == expected
    json.dumps(result)


def test_sanitize_dict_self_reference():
    """Dict that references itself should have the circular back-edge replaced with None."""
    d: dict[str, Any] = {"name": "adset_1", "id": "123"}
    d["source_adset"] = d  # circular reference
    result = sanitize_circular_references(d)
    assert result["name"] == "adset_1"
    assert result["id"] == "123"
    assert result["source_adset"] is None
    json.dumps(result)


def test_sanitize_nested_circular_reference():
    """Circular reference buried two levels deep."""
    inner: dict[str, Any] = {"value": 10}
    outer: dict[str, Any] = {"child": {"nested": inner}}
    inner["back_ref"] = outer  # circular: inner -> outer -> child -> nested -> inner
    result = sanitize_circular_references(outer)
    assert result["child"]["nested"]["value"] == 10
    assert result["child"]["nested"]["back_ref"] is None
    json.dumps(result)


def test_sanitize_list_circular_reference():
    """A list that contains itself should be sanitized."""
    lst: list[Any] = [1, 2]
    lst.append(lst)  # circular
    result = sanitize_circular_references(lst)
    assert result[0] == 1
    assert result[1] == 2
    assert result[2] is None
    json.dumps(result)


def test_sanitize_dict_in_list_circular():
    """Dict inside a list that references the parent dict."""
    parent: dict[str, Any] = {"items": []}
    parent["items"].append({"ref": parent})
    result = sanitize_circular_references(parent)
    assert result["items"][0]["ref"] is None
    json.dumps(result)


def test_sanitize_multiple_circular_paths():
    """Multiple distinct circular paths in the same structure."""
    a: dict[str, Any] = {"name": "a"}
    b: dict[str, Any] = {"name": "b"}
    a["ref_b"] = b
    b["ref_a"] = a  # circular a <-> b
    result = sanitize_circular_references(a)
    assert result["name"] == "a"
    assert result["ref_b"]["name"] == "b"
    assert result["ref_b"]["ref_a"] is None
    json.dumps(result)


def test_sanitize_shared_non_circular_dicts():
    """Same dict referenced multiple times (diamond) but no cycle should be preserved."""
    shared = {"x": 1}
    data = {"first": shared, "second": shared}
    result = sanitize_circular_references(data)
    assert result["first"] == {"x": 1}
    assert result["second"] == {"x": 1}
    json.dumps(result)


def test_sanitize_simulated_adset_export():
    """Simulate the real-world Facebook SDK AdSet circular reference pattern.

    AdSet._field_types has `source_adset: AdSet`, causing export_all_data()
    to produce a dict where a nested `source_adset` key points back to
    the parent dict.
    """
    adset_data: dict[str, Any] = {
        "id": "12345",
        "name": "My AdSet",
        "status": "ACTIVE",
        "daily_budget": "1000",
        "targeting": {"geo_locations": {"countries": ["US"]}},
    }
    adset_data["source_adset"] = adset_data

    result = sanitize_circular_references(adset_data)

    assert result["id"] == "12345"
    assert result["name"] == "My AdSet"
    assert result["status"] == "ACTIVE"
    assert result["daily_budget"] == "1000"
    assert result["targeting"] == {"geo_locations": {"countries": ["US"]}}
    assert result["source_adset"] is None
    serialized = json.dumps(result)
    assert "12345" in serialized


def test_read_records_sanitizes_circular_refs(api, some_config, mocker):
    """FBMarketingStream.read_records sanitizes circular references from export_all_data()."""
    from source_facebook_marketing.streams.base_streams import FBMarketingStream

    class TestStream(FBMarketingStream):
        def list_objects(self, params: Mapping[str, Any], account_id: str = None) -> Iterable:
            mock_obj = mocker.MagicMock(spec=AbstractObject)
            circular_data: dict[str, Any] = {"id": "999", "name": "test"}
            circular_data["self_ref"] = circular_data
            mock_obj.export_all_data.return_value = circular_data
            yield mock_obj

    stream = TestStream(api=api, account_ids=some_config["account_ids"])
    records = list(
        stream.read_records(
            sync_mode="full_refresh",
            stream_slice={"account_id": some_config["account_ids"][0], "stream_state": {}},
        )
    )
    assert len(records) == 1
    assert records[0]["id"] == "999"
    assert records[0]["name"] == "test"
    assert records[0]["self_ref"] is None
    json.dumps(records[0])
