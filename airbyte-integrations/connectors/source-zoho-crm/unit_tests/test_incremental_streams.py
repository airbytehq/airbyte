#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import pytest
from source_zoho_crm.streams import IncrementalZohoCrmStream as BaseIncrementalZohoCrmStream
from source_zoho_crm.streams import _parse_datetime
from source_zoho_crm.types import FieldMeta, ModuleMeta

from airbyte_cdk.models import SyncMode


@pytest.fixture
def stream_factory(mocker):
    def wrapper(stream_name, schema=None, module=None):
        class IncrementalZohoStream(BaseIncrementalZohoCrmStream):
            url_base = "https://dummy.com"
            _path = f"/crm/v2/{stream_name}"
            json_schema = schema or {}
            primary_key = "id"

        if module is not None:
            IncrementalZohoStream.module = module
        return IncrementalZohoStream(config={})

    return wrapper


def test_cursor_field(stream_factory):
    stream = stream_factory("Leads")
    assert stream.cursor_field == "Modified_Time"


def _make_field(api_name, data_type="text", json_type="string"):
    return FieldMeta(
        json_type=json_type,
        length=256,
        api_name=api_name,
        data_type=data_type,
        decimal_place=None,
        system_mandatory=False,
        display_label=api_name,
        pick_list_values=[],
    )


def test_cursor_field_resolved_from_module_fields(stream_factory):
    """When module has Action_Performed_Time but no Modified_Time, cursor resolves dynamically."""
    fields = [_make_field("id"), _make_field("Action_Performed_Time", data_type="datetime")]
    module = ModuleMeta(api_name="Actions_Performed", module_name="Actions Performed", api_supported=True, fields=fields)
    stream = stream_factory("Actions_Performed", module=module)
    assert stream.cursor_field == "Action_Performed_Time"


def test_cursor_field_prefers_modified_time(stream_factory):
    """When module has both Modified_Time and Action_Performed_Time, prefer Modified_Time."""
    fields = [
        _make_field("id"),
        _make_field("Modified_Time", data_type="datetime"),
        _make_field("Action_Performed_Time", data_type="datetime"),
    ]
    module = ModuleMeta(api_name="Leads", module_name="Leads", api_supported=True, fields=fields)
    stream = stream_factory("Leads", module=module)
    assert stream.cursor_field == "Modified_Time"


def test_cursor_field_fallback_to_any_datetime(stream_factory):
    """When module has no known cursor candidates, fall back to any datetime field."""
    fields = [_make_field("id"), _make_field("Created_At", data_type="datetime")]
    module = ModuleMeta(api_name="Custom", module_name="Custom", api_supported=True, fields=fields)
    stream = stream_factory("Custom", module=module)
    assert stream.cursor_field == "Created_At"


def test_updated_state(mocker, stream_factory):
    stream = stream_factory("Leads")
    assert stream.state == {"Modified_Time": "1970-01-01T00:00:00+00:00"}
    mocker.patch(
        "source_zoho_crm.streams.HttpStream.read_records",
        Mock(
            return_value=[
                {"Name": "Joan", "Surname": "Arc", "Modified_Time": "2021-12-12T13:15:09+02:00"},
                {"Name": "Jack", "Surname": "Sparrow", "Modified_Time": "2022-03-03T12:31:05+02:00"},
                {"Name": "Ron", "Surname": "Weasley", "Modified_Time": "2022-02-03T00:00:00+02:00"},
            ]
        ),
    )
    for _ in stream.read_records(SyncMode.incremental):
        # this is generator, so we have to exhaust it before asserting anything
        pass
    assert stream.state == {"Modified_Time": "2022-03-03T12:31:05+02:00"}


def test_updated_state_with_z_suffix(mocker, stream_factory):
    """Cursor values with Z suffix (UTC) are parsed correctly."""
    stream = stream_factory("Leads")
    mocker.patch(
        "source_zoho_crm.streams.HttpStream.read_records",
        Mock(
            return_value=[
                {"Name": "Alice", "Modified_Time": "2026-06-08T00:00:00Z"},
                {"Name": "Bob", "Modified_Time": "2026-06-09T12:00:00Z"},
            ]
        ),
    )
    for _ in stream.read_records(SyncMode.incremental):
        pass
    assert stream.state == {"Modified_Time": "2026-06-09T12:00:00+00:00"}


def test_read_records_missing_cursor_field(mocker, stream_factory):
    """Records missing the cursor field are yielded without crashing."""
    stream = stream_factory("Leads")
    mocker.patch(
        "source_zoho_crm.streams.HttpStream.read_records",
        Mock(
            return_value=[
                {"Name": "No Cursor"},
                {"Name": "Has Cursor", "Modified_Time": "2022-01-01T00:00:00+00:00"},
            ]
        ),
    )
    records = list(stream.read_records(SyncMode.incremental))
    assert len(records) == 2
    assert records[0] == {"Name": "No Cursor"}
    assert stream.state == {"Modified_Time": "2022-01-01T00:00:00+00:00"}


@pytest.mark.parametrize(
    ("state", "expected_header"),
    (
        pytest.param(
            {"Modified_Time": "2021-09-17T13:30:28-07:00"},
            {"If-Modified-Since": "2021-09-17T13:30:29-07:00"},
            id="with_offset",
        ),
        pytest.param(
            {},
            {"If-Modified-Since": "1970-01-01T00:00:01+00:00"},
            id="empty_state",
        ),
        pytest.param(
            {"Modified_Time": "2026-06-08T00:00:00Z"},
            {"If-Modified-Since": "2026-06-08T00:00:01+00:00"},
            id="z_suffix",
        ),
    ),
)
def test_request_headers(stream_factory, state, expected_header):
    stream = stream_factory("Leads")
    inputs = {"stream_slice": None, "stream_state": state, "next_page_token": None}
    assert stream.request_headers(**inputs) == expected_header


def test_supports_incremental(stream_factory):
    stream = stream_factory("Leads")
    assert stream.supports_incremental


def test_source_defined_cursor(stream_factory):
    stream = stream_factory("Leads")
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(stream_factory):
    stream = stream_factory("Leads")
    assert stream.state_checkpoint_interval is None


@pytest.mark.parametrize(
    ("input_value", "expected_offset"),
    (
        pytest.param("2021-09-17T13:30:28-07:00", "-07:00", id="negative_offset"),
        pytest.param("2021-09-17T13:30:28+02:00", "+02:00", id="positive_offset"),
        pytest.param("2021-09-17T13:30:28Z", "+00:00", id="z_suffix"),
        pytest.param("2021-09-17T13:30:28+00:00", "+00:00", id="explicit_utc"),
        pytest.param("1970-01-01T00:00:00+00:00", "+00:00", id="epoch"),
    ),
)
def test_parse_datetime(input_value, expected_offset):
    result = _parse_datetime(input_value)
    assert result.tzinfo is not None
    assert expected_offset in result.isoformat()
