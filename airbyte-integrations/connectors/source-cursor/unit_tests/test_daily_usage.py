# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from typing import Any, Mapping

import pytest
import yaml
from freezegun import freeze_time

from airbyte_cdk import ConfiguredAirbyteCatalog, SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
_DAILY_USAGE_URL = "https://api.cursor.com/teams/daily-usage-data"
_START_DATE_MS = 1_767_225_600_000
_END_DATE_MS = 1_767_312_000_000


def _catalog() -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream("daily_usage", SyncMode.incremental).build()


def _response(data: list[Mapping[str, Any]], page: int, has_next_page: bool) -> HttpResponse:
    return HttpResponse(
        json.dumps(
            {
                "data": data,
                "pagination": {
                    "page": page,
                    "pageSize": 100,
                    "totalUsers": 101,
                    "totalPages": 2,
                    "hasNextPage": has_next_page,
                    "hasPreviousPage": page > 1,
                },
            }
        )
    )


def test_daily_usage_paginates_from_response_metadata() -> None:
    first_page_request = HttpRequest(
        _DAILY_USAGE_URL,
        body={"endDate": _END_DATE_MS, "startDate": _START_DATE_MS, "page": 1, "pageSize": 100},
    )
    second_page_request = HttpRequest(
        _DAILY_USAGE_URL,
        body={"endDate": _END_DATE_MS, "startDate": _START_DATE_MS, "page": 2, "pageSize": 100},
    )
    active_users = [
        {
            "date": _START_DATE_MS,
            "day": "2026-01-01",
            "email": f"active-{user_id}@example.com",
            "userId": user_id,
            "isActive": True,
        }
        for user_id in range(1, 101)
    ]
    inactive_user = {
        "date": _START_DATE_MS,
        "day": "2026-01-01",
        "email": "inactive@example.com",
        "userId": 101,
        "isActive": False,
    }

    with HttpMocker() as http_mocker:
        http_mocker.post(first_page_request, _response(active_users, page=1, has_next_page=True))
        http_mocker.post(second_page_request, _response([inactive_user], page=2, has_next_page=False))

        with freeze_time("2026-01-02T00:00:00Z"):
            config = {"api_key": "crsr_test", "start_date": "2026-01-01"}
            catalog = _catalog()
            state = StateBuilder().build()
            source = YamlDeclarativeSource(path_to_yaml=str(_MANIFEST_PATH), catalog=catalog, config=config, state=state)
            output = entrypoint_read(source, config, catalog, state)

        assert len(output.records) == 101
        assert output.records[-1].record.data == inactive_user
        http_mocker.assert_number_of_calls(first_page_request, 1)
        http_mocker.assert_number_of_calls(second_page_request, 1)


@pytest.fixture(scope="module")
def manifest() -> Mapping[str, Any]:
    with _MANIFEST_PATH.open() as manifest_file:
        return yaml.safe_load(manifest_file)


def _stream(manifest: Mapping[str, Any], name: str) -> Mapping[str, Any]:
    return next(stream for stream in manifest["streams"] if stream["name"] == name)


def test_daily_usage_user_id_is_numeric(manifest: Mapping[str, Any]) -> None:
    properties = _stream(manifest, "daily_usage")["schema_loader"]["schema"]["properties"]

    assert properties["userId"]["type"] == ["number", "null"]


def test_spend_schema_includes_documented_numeric_fields(manifest: Mapping[str, Any]) -> None:
    properties = _stream(manifest, "spend")["schema_loader"]["schema"]["properties"]

    assert properties["overallSpendCents"]["type"] == ["number", "null"]
    for field in ("monthlyLimitDollars", "hardLimitOverrideDollars", "effectivePerUserLimitDollars"):
        assert properties[field]["type"] == ["number", "null"]


def test_error_handler_honors_retry_after_before_exponential_backoff(manifest: Mapping[str, Any]) -> None:
    strategies = manifest["definitions"]["linked"]["HttpRequester"]["error_handler"]["backoff_strategies"]

    assert strategies == [
        {"type": "WaitTimeFromHeader", "header": "Retry-After"},
        {"type": "ExponentialBackoffStrategy", "factor": 5},
    ]
