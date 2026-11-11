# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


MANIFEST = Path(__file__).parents[1] / "manifest.yaml"
CONFIG = {"username": "test-token-id", "password": "test-token-secret", "start_date": "2020-01-01T00:00:00Z"}


def read_stream(name, config=None, sync_mode=SyncMode.full_refresh, state=None):
    config = CONFIG if config is None else config
    catalog = CatalogBuilder().with_stream(name, sync_mode).build()
    source = YamlDeclarativeSource(str(MANIFEST), config=config, catalog=catalog, state=state)
    return read(source, config=config, catalog=catalog, state=state)


@pytest.mark.parametrize(
    "name,path,page_size",
    [
        ("video_assets", "video/v1/assets", 50),
        ("video_live-streams", "video/v1/live-streams", 50),
        ("system_signin-keys", "system/v1/signing-keys", 50),
        ("video_playback-restrictions", "video/v1/playback-restrictions", 50),
        ("video_transcription-vocabularies", "video/v1/transcription-vocabularies", 10),
        ("video_uploads", "video/v1/uploads", 50),
        ("video_signing-keys", "system/v1/signing-keys", 50),
    ],
)
def test_list_streams_paginate(name, path, page_size):
    records = [{"id": str(i), "created_at": "1609869152"} for i in range(page_size + 1)]
    first_page = HttpRequest(f"https://api.mux.com/{path}", query_params={"limit": str(page_size), "page": "1"})
    second_page = HttpRequest(f"https://api.mux.com/{path}", query_params={"limit": str(page_size), "page": "2"})
    with HttpMocker() as http_mocker:
        http_mocker.get(first_page, HttpResponse(body=json.dumps({"data": records[:page_size]})))
        http_mocker.get(second_page, HttpResponse(body=json.dumps({"data": records[page_size:]})))

        output = read_stream(name)

        assert output.errors == []
        assert [record.record.data for record in output.records] == records
        http_mocker.assert_number_of_calls(first_page, 1)
        http_mocker.assert_number_of_calls(second_page, 1)


@pytest.mark.parametrize(
    "name,path,page_size",
    [
        ("video_transcription-vocabularies", "video/v1/transcription-vocabularies", 10),
        ("video_signing-keys", "system/v1/signing-keys", 50),
    ],
)
@pytest.mark.parametrize("response_cursor,expected_cursor", [("1609869153", "1609869153"), ("1609869151", "1609869152")])
def test_changed_incremental_streams_resume_existing_state(name, path, page_size, response_cursor, expected_cursor):
    state = StateBuilder().with_stream_state(name, {"created_at": "1609869152"}).build()
    record = {"id": "record-id", "created_at": response_cursor}
    request = HttpRequest(f"https://api.mux.com/{path}", query_params={"limit": str(page_size), "page": "1"})
    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(body=json.dumps({"data": [record]})))

        output = read_stream(name, sync_mode=SyncMode.incremental, state=state)

        assert output.errors == []
        assert [message.record.data for message in output.records] == [record]
        assert vars(output.most_recent_state.stream_state) == {"created_at": expected_cursor}


@pytest.mark.parametrize("playback_config", [{}, {"playback_id": ""}])
def test_playbacks_without_optional_id_do_not_request(playback_config):
    with HttpMocker():
        output = read_stream("video_playbacks", {**CONFIG, **playback_config})

        assert output.errors == []
        assert output.records == []


def test_playbacks_read_single_object():
    request = HttpRequest("https://api.mux.com/video/v1/playback-ids/playback-id")
    record = {"id": "playback-id", "policy": "public", "object": {"type": "asset", "id": "asset-id"}}
    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(body=json.dumps({"data": record})))

        output = read_stream("video_playbacks", {**CONFIG, "playback_id": "playback-id"})

        assert output.errors == []
        assert [message.record.data for message in output.records] == [record]
        http_mocker.assert_number_of_calls(request, 1)


@pytest.mark.parametrize("status_code", [401, 403, 404])
def test_playbacks_do_not_hide_errors_for_configured_id(status_code):
    request = HttpRequest("https://api.mux.com/video/v1/playback-ids/invalid-id")
    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(body=json.dumps({"error": {"messages": ["Request failed"]}}), status_code=status_code))

        output = read_stream("video_playbacks", {**CONFIG, "playback_id": "invalid-id"})

        assert output.errors
        assert output.records == []
        http_mocker.assert_number_of_calls(request, 1)
