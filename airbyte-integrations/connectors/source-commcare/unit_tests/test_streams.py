#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from urllib.parse import parse_qs, urlparse

import pytest
from source_commcare.source import CommcareStream, Form, SourceCommcare

from airbyte_cdk.models import AirbyteStateBlob, SyncMode
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


BASE_URL = "https://www.commcarehq.org/a/space/api/v0.5/"
CONFIG = {
    "api_key": "k",
    "app_id": "app1",
    "project_space": "space",
    "start_date": "2022-01-01T00:00:00Z",
}
FORM_RECORD = {"id": "f1", "indexed_on": "2022-02-01T00:00:00.123456", "form": {"q1": "a"}}
CASE_RECORD = {"id": "c1", "indexed_on": "2022-02-02T00:00:00.654321", "xform_ids": ["f1"]}


@pytest.fixture(autouse=True)
def clear_form_ids():
    CommcareStream.forms.clear()
    yield
    CommcareStream.forms.clear()


def _form_args():
    return {
        "app_id": CONFIG["app_id"],
        "start_date": CONFIG["start_date"],
        "project_space": CONFIG["project_space"],
        "name": "Survey",
        "xmlns": "http://x/abcde",
        "schema": SourceCommcare().base_schema(),
        "authenticator": TokenAuthenticator(CONFIG["api_key"], auth_method="ApiKey"),
    }


def _mock_api(requests_mock):
    requests_mock.get(
        f"{BASE_URL}application/app1/",
        json={
            "modules": [
                {
                    "forms": [
                        {"xmlns": "http://x/abcde", "name": {"en": "Survey"}},
                    ]
                }
            ]
        },
    )
    requests_mock.get(f"{BASE_URL}form", json={"meta": {"next": None}, "objects": [FORM_RECORD]})
    requests_mock.get(f"{BASE_URL}case", json={"meta": {"next": None}, "objects": [CASE_RECORD]})


def _read_incremental(requests_mock, state=None):
    _mock_api(requests_mock)
    catalog = CatalogBuilder().with_stream("Survey", SyncMode.incremental).with_stream("zzz_case", SyncMode.incremental).build()
    output = read(SourceCommcare(), CONFIG, catalog, state)
    output.raise_if_errors()
    return output


def test_generate_streams_constructs_form_and_case():
    appdata = [
        {
            "modules": [
                {
                    "forms": [
                        {"xmlns": "http://x/abcde", "name": {"en": "Survey"}},
                        {"xmlns": "http://x/12345", "name": {}},
                    ]
                }
            ]
        }
    ]
    args = {"authenticator": TokenAuthenticator(CONFIG["api_key"], auth_method="ApiKey")}

    streams = SourceCommcare().generate_streams(args, CONFIG, appdata)

    assert [stream.name for stream in streams] == ["Survey", "Unnamed_12345", "zzz_case"]


def test_state_setter_ignores_empty_state():
    stream = Form(**_form_args())

    stream.state = {}

    assert stream.state == {"indexed_on": datetime(2022, 1, 1)}

    stream.state = {"indexed_on": "2022-01-15T00:00:00.500000"}

    assert stream.state == {"indexed_on": datetime(2022, 1, 15, 0, 0, 0, 500000)}


def test_incremental_read_without_state(requests_mock):
    output = _read_incremental(requests_mock)

    records = {message.record.stream: message.record.data for message in output.records}
    assert records == {
        "Survey": {
            "q1": "a",
            "streamname": "Survey",
            "xmlns": "http://x/abcde",
            "id": "f1",
            "indexed_on": "2022-02-01T00:00:00.123456Z",
        },
        "zzz_case": {
            "id": "c1",
            "indexed_on": "2022-02-02T00:00:00.654321Z",
            "streamname": "case",
            "xform_ids": "f1",
        },
    }

    state = {message.state.stream.stream_descriptor.name: message.state.stream.stream_state for message in output.state_messages}
    assert state == {
        "Survey": AirbyteStateBlob({"indexed_on": "2022-02-01T00:00:00.123456"}),
        "zzz_case": AirbyteStateBlob({"indexed_on": "2022-02-02T00:00:00.654321"}),
    }

    form_request = next(request for request in requests_mock.request_history if urlparse(request.url).path.endswith("/form"))
    assert parse_qs(urlparse(form_request.url).query) == {
        "format": ["json"],
        "app_id": ["app1"],
        "indexed_on_start": ["2022-01-01T00:00:00.000000"],
        "order_by": ["indexed_on"],
        "limit": ["1000"],
        "xmlns": ["http://x/abcde"],
    }


def test_incremental_read_with_state(requests_mock):
    state = StateBuilder().with_stream_state("Survey", {"indexed_on": "2022-01-15T00:00:00.500000"}).build()

    output = _read_incremental(requests_mock, state)

    form_request = next(request for request in requests_mock.request_history if urlparse(request.url).path.endswith("/form"))
    assert parse_qs(urlparse(form_request.url).query)["indexed_on_start"] == ["2022-01-15T00:00:00.500000"]

    form_state = next(
        message.state.stream.stream_state for message in output.state_messages if message.state.stream.stream_descriptor.name == "Survey"
    )
    assert form_state == AirbyteStateBlob({"indexed_on": "2022-02-01T00:00:00.123456"})
