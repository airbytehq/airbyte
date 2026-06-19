#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from source_zoho_crm.streams import IncrementalZohoCrmStream as BaseIncrementalZohoCrmStream
from source_zoho_crm.streams import parse_iso

from airbyte_cdk.models import SyncMode


@pytest.fixture
def stream_factory(mocker):
    def wrapper(stream_name, schema=None):
        class IncrementalZohoStream(BaseIncrementalZohoCrmStream):
            url_base = "https://dummy.com"
            _path = f"/crm/v2/{stream_name}"
            json_schema = schema or {}
            primary_key = "id"

        return IncrementalZohoStream(config={})

    return wrapper


def test_cursor_field(stream_factory):
    stream = stream_factory("Leads")
    assert stream.cursor_field == "Modified_Time"


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


@pytest.mark.parametrize(
    ("state", "expected_header"),
    (
        ({"Modified_Time": "2021-09-17T13:30:28-07:00"}, {"If-Modified-Since": "2021-09-17T13:30:29-07:00"}),
        ({}, {"If-Modified-Since": "1970-01-01T00:00:01+00:00"}),
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


def _module_with_fields(*api_names):
    """Build a fake module whose .fields expose the given api_names."""
    fields = [SimpleNamespace(api_name=name) for name in api_names]
    return SimpleNamespace(fields=fields)


def _incremental_stream_with_module(module):
    class _Stream(BaseIncrementalZohoCrmStream):
        url_base = "https://dummy.com"
        primary_key = "id"

    stream = _Stream(config={})
    stream.module = module
    return stream


def test_parse_iso_accepts_z_suffix():
    # Bug 1: fromisoformat on py<=3.10 rejects "Z"; parse_iso must accept it.
    parsed_z = parse_iso("2026-06-08T00:00:00Z")
    parsed_offset = parse_iso("2026-06-08T00:00:00+00:00")
    assert parsed_z == parsed_offset


def test_parse_iso_passes_through_non_strings():
    sentinel = object()
    assert parse_iso(sentinel) is sentinel


def test_cursor_field_defaults_to_modified_time():
    stream = _incremental_stream_with_module(_module_with_fields("Modified_Time", "Created_Time"))
    assert stream.cursor_field == "Modified_Time"


def test_cursor_field_resolves_module_specific_cursor():
    # Bug 2: Actions_Performed has no Modified_Time; uses Action_Performed_Time.
    stream = _incremental_stream_with_module(_module_with_fields("Action_Performed_Time", "Action_Type"))
    assert stream.cursor_field == "Action_Performed_Time"


def test_read_records_passes_through_record_without_cursor(mocker):
    # A record lacking the resolved cursor should be yielded, not crash the stream.
    stream = _incremental_stream_with_module(_module_with_fields("Modified_Time"))
    mocker.patch(
        "source_zoho_crm.streams.HttpStream.read_records",
        Mock(return_value=[{"Name": "NoCursorHere"}]),
    )
    records = list(stream.read_records(SyncMode.incremental))
    assert records == [{"Name": "NoCursorHere"}]
