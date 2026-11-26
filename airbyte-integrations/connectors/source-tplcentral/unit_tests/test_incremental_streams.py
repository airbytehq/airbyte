#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from urllib.parse import parse_qs, urlparse

import pytest
from source_tplcentral.source import SourceTplcentral
from source_tplcentral.streams import IncrementalTplcentralStream

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


@pytest.fixture
def config():
    return {
        "config": {
            "authenticator": None,
            "url_base": "https://secure-wms.com/",
            "client_id": "xxx",
            "client_secret": "yyy",
            "user_login_id": 123,
            "tpl_key": "{00000000-0000-0000-0000-000000000000}",
            "customer_id": 4,
            "facility_id": 5,
            "start_date": "2021-10-01",
        }
    }


@pytest.fixture
def patch_incremental_base_class(mocker):
    mocker.patch.object(IncrementalTplcentralStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalTplcentralStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalTplcentralStream, "cursor_field", "test_cursor_field")
    mocker.patch.object(IncrementalTplcentralStream, "collection_field", "CollectionField")
    mocker.patch.object(IncrementalTplcentralStream, "__abstractmethods__", set())


@pytest.fixture
def stream(patch_incremental_base_class, config):
    return IncrementalTplcentralStream(**config)


def test_cursor_field(stream):
    expected_cursor_field = "test_cursor_field"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(stream):
    inputs = {
        "current_stream_state": {
            "test_cursor_field": "2021-01-01T01:02:34+01:56",
        },
        "latest_record": {},
    }
    expected_state = {"test_cursor_field": "2021-01-01T01:02:34+01:56"}
    assert stream.get_updated_state(**inputs) == expected_state

    inputs = {
        "current_stream_state": {},
        "latest_record": {
            "test_cursor_field": "2021-01-01T01:02:34+01:56",
        },
    }
    expected_state = {"test_cursor_field": "2021-01-01T01:02:34+01:56"}
    assert stream.get_updated_state(**inputs) == expected_state

    inputs = {
        "current_stream_state": {
            "test_cursor_field": "2021-01-01T01:02:34+01:56",
        },
        "latest_record": {
            "test_cursor_field": "2021-01-01T01:02:34+01:57",
        },
    }
    expected_state = {"test_cursor_field": "2021-01-01T01:02:34"}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(stream, config):
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    expected_stream_slice = [{"test_cursor_field": config["config"]["start_date"]}]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(stream):
    assert stream.supports_incremental


def test_source_defined_cursor(stream):
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(stream):
    expected_checkpoint_interval = 100
    assert stream.state_checkpoint_interval == expected_checkpoint_interval


def test_incremental_read_emits_records_and_state(requests_mock, config):
    source_config = {key: value for key, value in config["config"].items() if key != "authenticator"}
    requests_mock.post(
        f"{source_config['url_base']}AuthServer/api/Token",
        json={"access_token": "the_token", "token_type": "Bearer", "expires_in": 3600},
    )
    requests_mock.get(
        "https://secure-wms.com/customers/4/items",
        json={
            "TotalResults": 2,
            "ResourceList": [
                {"ItemId": 1, "ReadOnly": {"LastModifiedDate": "2021-10-05T00:00:00"}},
                {"ItemId": 2, "ReadOnly": {"LastModifiedDate": "2021-10-06T12:00:00"}},
            ],
        },
    )

    catalog = CatalogBuilder().with_stream("items", SyncMode.incremental).build()
    state = StateBuilder().with_stream_state("items", {"_cursor": "2021-10-03T00:00:00"}).build()
    output = read(SourceTplcentral(), source_config, catalog, state)

    assert [message.record.data for message in output.records] == [
        {
            "ItemId": 1,
            "ReadOnly": {"LastModifiedDate": "2021-10-05T00:00:00"},
            "_id": 1,
            "_cursor": "2021-10-05T00:00:00",
        },
        {
            "ItemId": 2,
            "ReadOnly": {"LastModifiedDate": "2021-10-06T12:00:00"},
            "_id": 2,
            "_cursor": "2021-10-06T12:00:00",
        },
    ]
    assert output.state_messages[-1].state.stream.stream_state._cursor == "2021-10-06T12:00:00"
    assert output.errors == []

    request = requests_mock.request_history[-1]
    assert parse_qs(urlparse(request.url).query) == {
        "sort": ["ReadOnly.LastModifiedDate"],
        "rql": ["ReadOnly.LastModifiedDate=ge=2021-10-03T00:00:00"],
    }


@pytest.mark.parametrize("status_code", [429, 500])
def test_incremental_read_retries_transient_errors(requests_mock, config, monkeypatch, status_code):
    monkeypatch.setattr("time.sleep", lambda *_: None)
    source_config = {key: value for key, value in config["config"].items() if key != "authenticator"}
    requests_mock.post(
        f"{source_config['url_base']}AuthServer/api/Token",
        json={"access_token": "the_token", "token_type": "Bearer", "expires_in": 3600},
    )
    items_url = "https://secure-wms.com/customers/4/items"
    items_response = {
        "TotalResults": 2,
        "ResourceList": [
            {"ItemId": 1, "ReadOnly": {"LastModifiedDate": "2021-10-05T00:00:00"}},
            {"ItemId": 2, "ReadOnly": {"LastModifiedDate": "2021-10-06T12:00:00"}},
        ],
    }
    requests_mock.get(
        items_url,
        [{"status_code": status_code, "json": {}}, {"json": items_response}],
    )

    catalog = CatalogBuilder().with_stream("items", SyncMode.incremental).build()
    state = StateBuilder().with_stream_state("items", {"_cursor": "2021-10-03T00:00:00"}).build()
    output = read(SourceTplcentral(), source_config, catalog, state)

    assert [message.record.data for message in output.records] == [
        {
            "ItemId": 1,
            "ReadOnly": {"LastModifiedDate": "2021-10-05T00:00:00"},
            "_id": 1,
            "_cursor": "2021-10-05T00:00:00",
        },
        {
            "ItemId": 2,
            "ReadOnly": {"LastModifiedDate": "2021-10-06T12:00:00"},
            "_id": 2,
            "_cursor": "2021-10-06T12:00:00",
        },
    ]
    assert output.errors == []
    items_requests = [
        request for request in requests_mock.request_history if request.method == "GET" and request.url.split("?")[0] == items_url
    ]
    assert len(items_requests) == 2


@pytest.mark.parametrize("status_code", [403, 404])
def test_incremental_read_does_not_retry_client_errors(requests_mock, config, status_code):
    source_config = {key: value for key, value in config["config"].items() if key != "authenticator"}
    requests_mock.post(
        f"{source_config['url_base']}AuthServer/api/Token",
        json={"access_token": "the_token", "token_type": "Bearer", "expires_in": 3600},
    )
    items_url = "https://secure-wms.com/customers/4/items"
    requests_mock.get(items_url, status_code=status_code, json={})

    catalog = CatalogBuilder().with_stream("items", SyncMode.incremental).build()
    state = StateBuilder().with_stream_state("items", {"_cursor": "2021-10-03T00:00:00"}).build()
    output = read(SourceTplcentral(), source_config, catalog, state, expecting_exception=True)

    assert output.records == []
    assert output.errors
    items_requests = [
        request for request in requests_mock.request_history if request.method == "GET" and request.url.split("?")[0] == items_url
    ]
    assert len(items_requests) == 1
