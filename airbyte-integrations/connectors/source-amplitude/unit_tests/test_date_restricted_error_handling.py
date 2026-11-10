# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONNECTOR_DIR = Path(__file__).parent.parent
sys.path.append(str(_CONNECTOR_DIR))
_CONFIG = {
    "api_key": "an-api-key",
    "secret_key": "a-secret-key",
    "start_date": "2025-10-31T00:00:00Z",
    "active_users_group_by_country": False,
}
_BASE_MESSAGE = "Amplitude rejected the requested date range because it is older than the project's data retention limit"
_DETAILS = "2025-10-31 is before cutoff date of 2025-11-09"
_METADATA = {"details": _DETAILS, "cutoff_date": "2025-11-09"}
_FALLBACK = "Set the Start Date within the project's data retention period."
_GENERIC_MESSAGE = "Access denied due to lack of permission or invalid API/Secret key or wrong data region."


@pytest.mark.parametrize(
    "stream,path,params",
    [
        ("average_session_length", "/2/sessions/average", {"start": "20251031", "end": "20251101"}),
        ("active_users", "/2/users", {"start": "20251031", "end": "20251101", "m": "active", "i": "1", "g": ""}),
        ("events", "/2/export", {"start": "20251031T00", "end": "20251101T00"}),
    ],
)
@pytest.mark.parametrize(
    "body,expected_message",
    [
        (
            {"error": {"type": "date restricted", "message": "Date too far back", "metadata": _METADATA}},
            f"{_BASE_MESSAGE}: {_DETAILS}. Set the Start Date on or after 2025-11-09.",
        ),
        (
            {"type": "date restricted", "message": "Date too far back", "metadata": _METADATA},
            f"{_BASE_MESSAGE}: {_DETAILS}. Set the Start Date on or after 2025-11-09.",
        ),
        (
            {"error": "Forbidden", "type": "date restricted", "metadata": _METADATA},
            f"{_BASE_MESSAGE}: {_DETAILS}. Set the Start Date on or after 2025-11-09.",
        ),
        ({"error": {"type": "date restricted"}}, f"{_BASE_MESSAGE}. {_FALLBACK}"),
        ({"type": "date restricted", "metadata": None}, f"{_BASE_MESSAGE}. {_FALLBACK}"),
        (
            {"type": "date restricted", "metadata": {"cutoff_date": "2025-11-09"}},
            f"{_BASE_MESSAGE}. Set the Start Date on or after 2025-11-09.",
        ),
        (
            {"type": "date restricted", "metadata": {"details": _DETAILS}},
            f"{_BASE_MESSAGE}: {_DETAILS}. {_FALLBACK}",
        ),
        ({"error": "Forbidden"}, _GENERIC_MESSAGE),
        ({"error": {"type": "forbidden", "message": "Permission denied"}}, _GENERIC_MESSAGE),
        ({}, _GENERIC_MESSAGE),
    ],
)
@freeze_time("2025-11-01T00:00:00Z")
def test_403_reports_retention_or_permission_error(stream: str, path: str, params: dict, body: dict, expected_message: str) -> None:
    catalog = CatalogBuilder().with_stream(stream, SyncMode.incremental).build()
    source = YamlDeclarativeSource(config=_CONFIG, catalog=catalog, state=None, path_to_yaml=str(_CONNECTOR_DIR / "manifest.yaml"))
    with HttpMocker() as http_mocker:
        request = HttpRequest(url=f"https://amplitude.com/api{path}", query_params=params)
        http_mocker.get(request, HttpResponse(json.dumps(body), status_code=403))
        output = read(source, _CONFIG, catalog, None, True)
        http_mocker.assert_number_of_calls(request, 1)

    assert output.errors[0].trace.error.failure_type == FailureType.config_error
    assert output.errors[0].trace.error.message == expected_message
    assert not output.records
