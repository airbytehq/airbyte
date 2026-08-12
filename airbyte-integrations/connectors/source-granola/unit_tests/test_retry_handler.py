# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from pathlib import Path
from unittest.mock import patch

import pytest
import requests_mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams.http import rate_limiting
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


def _get_manifest_path() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_MANIFEST_PATH = _get_manifest_path() / "manifest.yaml"
_CONFIG = {"api_key": "test_key", "start_date": "2026-08-11"}
_BASE_URL = "https://public-api.granola.ai"
_NOTES_URL = f"{_BASE_URL}/v1/notes"
_SUCCESS_RESPONSE = {"notes": [{"id": "note-1"}], "cursor": "", "hasMore": False}


def _sync_notes():
    catalog = CatalogBuilder().with_stream("notes", SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=catalog,
        config=_CONFIG,
        state=StateBuilder().build(),
    )
    return read(source, _CONFIG, catalog)


# The CDK sleeps for the backoff time plus one second to cover fractions of a second,
# so a Retry-After of 7 sleeps 8s and the first exponential interval (factor 5) sleeps 11s.
@pytest.mark.parametrize(
    "retryable_response,expected_sleep",
    [
        pytest.param({"status_code": 429, "headers": {"Retry-After": "7"}}, 8.0, id="429_with_retry_after_header"),
        pytest.param({"status_code": 429}, 11.0, id="429_without_retry_after_header"),
        pytest.param({"status_code": 500}, 11.0, id="500_server_error"),
    ],
)
def test_retryable_response_is_retried_with_configured_backoff(retryable_response, expected_sleep):
    with requests_mock.Mocker() as mocker, patch.object(rate_limiting.time, "sleep") as sleep:
        mocker.get(_NOTES_URL, [retryable_response, {"status_code": 200, "json": _SUCCESS_RESPONSE}])

        output = _sync_notes()

    assert [record.record.data["id"] for record in output.records] == ["note-1"]
    assert mocker.call_count == 2
    assert sleep.call_args_list[0].args == (expected_sleep,)
