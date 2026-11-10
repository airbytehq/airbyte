# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path

import pytest
import requests_mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


API_KEY = "test-key"
CONFIG = {"api_key": API_KEY, "stats_start_date": "2026-09-01T00:00:00Z"}
BASE = "https://api.mention.net/api"
INVALID_TOKEN = {"error": "invalid_token", "error_description": "The access token provided is invalid."}

RESPONSES = {
    "/api/accounts/me": {"account": {"id": "acc-1", "name": "Airbyte"}},
    "/api/accounts/acc-1/alerts": {"alerts": [{"id": 11}, {"id": 12}], "_links": {}},
}


def mention_api(request, context):
    if request.headers.get("Authorization") != f"Bearer {API_KEY}":
        context.status_code = 401
        return json.dumps(INVALID_TOKEN)
    context.status_code = 200
    return json.dumps(RESPONSES[request.path])


@pytest.mark.parametrize(
    "stream_name, expected_ids, expected_paths",
    [
        ("account_me", ["acc-1"], ["/api/accounts/me"]),
        ("alert", [11, 12], ["/api/accounts/me", "/api/accounts/acc-1/alerts"]),
    ],
)
def test_read_sends_api_key_as_bearer_token(stream_name, expected_ids, expected_paths):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(
        path_to_yaml=str(Path(__file__).parents[2] / "manifest.yaml"), config=CONFIG, catalog=catalog, state=None
    )
    with requests_mock.Mocker() as mocker:
        mocker.get(requests_mock.ANY, text=mention_api)
        output = read(source, config=CONFIG, catalog=catalog, expecting_exception=True)

    assert output.errors == []
    assert [record.record.data["id"] for record in output.records] == expected_ids
    assert [request.path for request in mocker.request_history] == expected_paths
    assert {request.headers["Authorization"] for request in mocker.request_history} == {f"Bearer {API_KEY}"}
