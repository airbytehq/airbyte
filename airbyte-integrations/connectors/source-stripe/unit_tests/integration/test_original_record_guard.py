# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import yaml
from unit_tests.conftest import _YAML_FILE_PATH

from airbyte_cdk.sources.declarative.models.declarative_component_schema import AddFields as AddFieldsModel
from airbyte_cdk.sources.declarative.parsers.manifest_component_transformer import ManifestComponentTransformer
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory


_STREAMS = ["invoice_line_items", "subscription_items"]
_UPDATED_FIELD_BY_STREAM = {
    "invoice_line_items": "invoice_updated",
    "subscription_items": "subscription_updated",
}
_ID_FIELD_BY_STREAM = {
    "invoice_line_items": "invoice_id",
    "subscription_items": None,
}
_EVENT_TYPE_BY_STREAM = {
    "invoice_line_items": {
        "created": "invoice.created",
        "updated": "invoice.updated",
        "deleted": "invoice.deleted",
        "id": "in_1",
    },
    "subscription_items": {
        "created": "customer.subscription.created",
        "updated": "customer.subscription.updated",
        "deleted": "customer.subscription.deleted",
        "id": "sub_1",
    },
}


def _get_add_fields_transformations(stream_name: str):
    manifest = yaml.safe_load(_YAML_FILE_PATH.read_text())
    transformations = manifest["definitions"]["streams"][stream_name]["incremental_stream"]["transformations"]
    transformer = ManifestComponentTransformer()
    factory = ModelToComponentFactory()
    return [
        factory.create_component(AddFieldsModel, transformer.propagate_types_and_parameters("", transformation, {}), {})
        for transformation in transformations
        if transformation["type"] == "AddFields"
    ]


def _transform(stream_name: str, record: dict) -> dict:
    record = dict(record)
    for component in _get_add_fields_transformations(stream_name):
        component.transform(record, config={})
    return record


def _event_record(stream_name: str, event_kind: str) -> dict:
    events = _EVENT_TYPE_BY_STREAM[stream_name]
    return {
        "id": "li_1",
        "original_record": {
            "id": "evt_1",
            "type": events[event_kind],
            "created": 1700000000,
            "data": {"object": {"id": events["id"]}},
        },
    }


@pytest.mark.parametrize(
    "stream_name,record",
    [
        pytest.param("invoice_line_items", {"id": "li_1"}, id="invoice_line_items_missing_original_record"),
        pytest.param("subscription_items", {"id": "li_1"}, id="subscription_items_missing_original_record"),
        pytest.param("invoice_line_items", {"id": "li_1", "original_record": {}}, id="invoice_line_items_empty_original_record"),
        pytest.param("subscription_items", {"id": "li_1", "original_record": {}}, id="subscription_items_empty_original_record"),
        pytest.param("invoice_line_items", {"id": "li_1", "original_record": None}, id="invoice_line_items_none_original_record"),
        pytest.param("subscription_items", {"id": "li_1", "original_record": None}, id="subscription_items_none_original_record"),
    ],
)
def test_transformations_skip_records_without_original_record(stream_name: str, record: dict):
    transformed = _transform(stream_name, record)
    assert _UPDATED_FIELD_BY_STREAM[stream_name] not in transformed
    id_field = _ID_FIELD_BY_STREAM[stream_name]
    if id_field:
        assert id_field not in transformed
    assert "is_deleted" not in transformed


@pytest.mark.parametrize(
    "stream_name,event_kind,expected_updated",
    [
        pytest.param("invoice_line_items", "created", 1699999999, id="invoice_line_items_created_event"),
        pytest.param("subscription_items", "created", 1699999999, id="subscription_items_created_event"),
        pytest.param("invoice_line_items", "updated", 1700000000, id="invoice_line_items_updated_event"),
        pytest.param("subscription_items", "updated", 1700000000, id="subscription_items_updated_event"),
    ],
)
def test_transformations_apply_on_event_records(stream_name: str, event_kind: str, expected_updated: int):
    transformed = _transform(stream_name, _event_record(stream_name, event_kind))
    assert transformed[_UPDATED_FIELD_BY_STREAM[stream_name]] == expected_updated
    id_field = _ID_FIELD_BY_STREAM[stream_name]
    if id_field:
        assert transformed[id_field] == _EVENT_TYPE_BY_STREAM[stream_name]["id"]
    assert "is_deleted" not in transformed


@pytest.mark.parametrize(
    "stream_name",
    [
        pytest.param("invoice_line_items", id="invoice_line_items_deleted_event"),
        pytest.param("subscription_items", id="subscription_items_deleted_event"),
    ],
)
def test_transformations_mark_deleted_events(stream_name: str):
    transformed = _transform(stream_name, _event_record(stream_name, "deleted"))
    assert transformed["is_deleted"] is True
    assert transformed[_UPDATED_FIELD_BY_STREAM[stream_name]] == 1700000000
    id_field = _ID_FIELD_BY_STREAM[stream_name]
    if id_field:
        assert transformed[id_field] == _EVENT_TYPE_BY_STREAM[stream_name]["id"]


@pytest.mark.parametrize(
    "stream_name",
    [
        pytest.param("invoice_line_items", id="invoice_line_items_remain_original_record"),
        pytest.param("subscription_items", id="subscription_items_remain_original_record"),
    ],
)
def test_events_retriever_keeps_original_record(stream_name: str):
    manifest = yaml.safe_load(_YAML_FILE_PATH.read_text())
    record_expander = manifest["definitions"]["streams"][stream_name]["incremental_stream"]["retriever"]["record_selector"]["extractor"][
        "record_expander"
    ]
    assert record_expander["remain_original_record"] is True
