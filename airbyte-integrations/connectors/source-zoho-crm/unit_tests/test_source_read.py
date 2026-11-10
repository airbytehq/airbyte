# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from json import dumps
from urllib.parse import parse_qs, urlparse

import pytest
from source_zoho_crm.source import SourceZohoCrm

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover, read
from airbyte_cdk.test.state_builder import StateBuilder


OAUTH_URL = "https://accounts.zoho.com/oauth/v2/token"
API_BASE_URL = "https://zohoapis.com"
MODULES_URL = f"{API_BASE_URL}/crm/v2/settings/modules"
MODULE_A = "ModuleA"
MODULE_B = "ModuleB"
DATA_URL = f"{API_BASE_URL}/crm/v2/{MODULE_A}"
START_STATE = {"Modified_Time": "2024-01-01T00:00:00+00:00"}

CONFIG = {
    "client_id": "dummy-client-id",
    "client_secret": "dummy-client-secret",
    "refresh_token": "dummy-refresh-token",
    "dc_region": "US",
    "environment": "Production",
    "start_datetime": "2023-01-01T00:00:00+00:00",
    "max_concurrent_requests": 1,
}


@pytest.fixture
def zoho_api(requests_mock):
    requests_mock.post(OAUTH_URL, json={"access_token": "tok", "expires_in": 3600})
    requests_mock.get(
        MODULES_URL,
        json={
            "modules": [
                {"api_name": MODULE_A, "module_name": "Module A", "api_supported": True},
                {"api_name": MODULE_B, "module_name": "Module B", "api_supported": True},
            ]
        },
    )
    requests_mock.get(
        f"{API_BASE_URL}/crm/v2/settings/modules/{MODULE_A}",
        json={"modules": [{"api_name": MODULE_A, "module_name": "Module A", "api_supported": True}]},
    )
    requests_mock.get(f"{API_BASE_URL}/crm/v2/settings/modules/{MODULE_B}", status_code=204)
    requests_mock.get(
        f"{API_BASE_URL}/crm/v2/settings/fields",
        json={
            "fields": [
                {
                    "json_type": "string",
                    "length": 256,
                    "api_name": "Name",
                    "data_type": "text",
                    "decimal_place": None,
                    "system_mandatory": True,
                    "display_label": "Name",
                },
                {
                    "json_type": "string",
                    "length": 32,
                    "api_name": "Modified_Time",
                    "data_type": "datetime",
                    "decimal_place": None,
                    "system_mandatory": False,
                    "display_label": "Modified Time",
                },
            ]
        },
        additional_matcher=lambda request: request.qs.get("module") == [MODULE_A.lower()],
    )
    return requests_mock


def _discover_streams():
    return discover(SourceZohoCrm(), CONFIG).catalog.catalog.streams


def _read_stream(stream_name, state=None):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    state_messages = StateBuilder().with_stream_state(stream_name, state).build() if state is not None else StateBuilder().build()
    return read(SourceZohoCrm(), CONFIG, catalog, state=state_messages)


def _data_requests(requests_mock):
    return [request for request in requests_mock.request_history if urlparse(request.url).path == f"/crm/v2/{MODULE_A}"]


def test_discover_only_includes_modules_with_schema_and_uses_module_cursor(zoho_api):
    streams = _discover_streams()

    assert len(streams) == 1
    stream = streams[0]
    assert SyncMode.incremental in stream.supported_sync_modes
    assert stream.source_defined_cursor
    assert stream.default_cursor_field == ["Modified_Time"]


def test_oauth_refresh_uses_query_params_and_data_requests_use_zoho_auth(zoho_api):
    stream_name = _discover_streams()[0].name
    zoho_api.get(DATA_URL, json={"data": [], "info": {"more_records": False, "page": 1}})

    output = _read_stream(stream_name)

    token_requests = [request for request in zoho_api.request_history if urlparse(request.url).path == "/oauth/v2/token"]
    assert token_requests
    for request in token_requests:
        assert parse_qs(urlparse(request.url).query) == {
            "refresh_token": ["dummy-refresh-token"],
            "client_id": ["dummy-client-id"],
            "client_secret": ["dummy-client-secret"],
            "grant_type": ["refresh_token"],
        }
        assert request.body in (None, "")
    assert not output.errors
    data_requests = _data_requests(zoho_api)
    assert data_requests
    assert all(request.headers["Authorization"] == "Zoho-oauthtoken tok" for request in data_requests)


def test_incremental_read_sends_state_paginates_and_emits_latest_state(zoho_api):
    stream_name = _discover_streams()[0].name
    records = [
        {"id": "1", "Name": "First", "Modified_Time": "2024-01-01T00:00:02+00:00"},
        {"id": "2", "Name": "Second", "Modified_Time": "2024-01-01T00:00:03+00:00"},
    ]

    def data_response(request, context):
        if request.qs.get("page") == ["2"]:
            return dumps({"data": [records[1]], "info": {"more_records": False, "page": 2}})
        return dumps({"data": [records[0]], "info": {"more_records": True, "page": 1}})

    zoho_api.get(DATA_URL, text=data_response)
    output = _read_stream(stream_name, START_STATE)

    assert [message.record.data for message in output.records] == records
    sync_requests = [
        request for request in _data_requests(zoho_api) if request.headers.get("If-Modified-Since") == "2024-01-01T00:00:01+00:00"
    ]
    assert len(sync_requests) == 2
    assert sync_requests[0].headers["If-Modified-Since"] == "2024-01-01T00:00:01+00:00"
    assert sync_requests[1].qs["page"] == ["2"]
    assert output.most_recent_state.stream_descriptor.name == stream_name
    assert output.most_recent_state.stream_state.__dict__ == {"Modified_Time": "2024-01-01T00:00:03+00:00"}


def test_incremental_read_treats_304_as_empty_success(zoho_api):
    stream_name = _discover_streams()[0].name
    zoho_api.get(DATA_URL, status_code=304, text="")

    output = _read_stream(stream_name, START_STATE)

    assert not output.records
    assert not output.errors
    assert not [message for message in output.trace_messages if message.trace.type == "ERROR"]
