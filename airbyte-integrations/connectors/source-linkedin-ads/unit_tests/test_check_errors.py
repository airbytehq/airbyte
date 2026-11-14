# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
import sys
from pathlib import Path
from typing import Any

import pytest
import requests
import yaml

from airbyte_cdk.models import FailureType, Status
from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.streams.http.error_handlers import ResponseAction
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

from .conftest import get_source
from .utils import run_read


_CONFIG = {
    "start_date": "2021-01-01",
    "account_ids": [],
    "credentials": {"auth_method": "access_token", "access_token": "test_token"},
}
_URL = "https://api.linkedin.com/rest/adAccounts"
_LOGGER = logging.getLogger("airbyte")


def _assert_check_failure(config: dict, hint: str) -> None:
    source = get_source(config)
    result = source.check(_LOGGER, config)
    assert result.status == Status.FAILED
    assert hint in result.message
    accounts = next(stream for stream in source.streams(config) if stream.name == "accounts")
    with pytest.raises(AirbyteTracedException) as error:
        run_read(accounts)
    assert error.value.failure_type == FailureType.config_error
    assert hint in error.value.message


@pytest.mark.parametrize(
    "status,body,hint",
    [
        (401, {"message": "The token used in the request has expired"}, "Re-authenticate the source"),
        (401, {}, "Re-authenticate the source"),
        (403, {}, "r_ads scope"),
        (403, {"message": "Not enough permissions: r_ads"}, "r_ads scope"),
        (403, {"message": "Missing scope rw_ads"}, "rw_ads scope"),
        (403, {"message": "Missing scope r_ads_reporting"}, "r_ads_reporting scope"),
        (403, {"scope": "rw_ads", "message": "Access denied"}, "rw_ads scope"),
    ],
)
def test_check_authentication_errors(requests_mock: Any, status: int, body: dict, hint: str) -> None:
    requests_mock.get(_URL, status_code=status, json=body)
    _assert_check_failure(_CONFIG, hint)


@pytest.mark.parametrize("status", [401, 403])
def test_check_non_json_errors(requests_mock: Any, status: int) -> None:
    requests_mock.get(_URL, status_code=status, text="sensitive upstream response")
    _assert_check_failure(_CONFIG, "Re-authenticate")
    result = get_source(_CONFIG).check(_LOGGER, _CONFIG)
    assert "sensitive" not in result.message


@pytest.mark.parametrize("account_ids", [[], [123]])
def test_check_zero_accounts(requests_mock: Any, account_ids: list[int]) -> None:
    config = {**_CONFIG, "account_ids": account_ids}
    requests_mock.get(_URL, json={"elements": []})
    assert get_source(config).check(_LOGGER, config).status == Status.SUCCEEDED


@pytest.mark.parametrize("account_ids", [[], [123]])
def test_read_zero_accounts(requests_mock: Any, account_ids: list[int]) -> None:
    config = {**_CONFIG, "account_ids": account_ids}
    requests_mock.get(_URL, json={"elements": []})
    source = get_source(config)
    assert source.check(_LOGGER, config).status == Status.SUCCEEDED
    accounts = next(stream for stream in source.streams(config) if stream.name == "accounts")
    assert run_read(accounts) == []


def test_check_accessible_accounts(requests_mock: Any) -> None:
    requests_mock.get(_URL, json={"elements": [{"id": 1}]})
    assert get_source(_CONFIG).check(_LOGGER, _CONFIG).status == Status.SUCCEEDED


def test_check_without_custom_components(requests_mock: Any, monkeypatch: Any) -> None:
    monkeypatch.delenv("AIRBYTE_ENABLE_UNSAFE_CODE", raising=False)
    monkeypatch.setitem(sys.modules, "source_declarative_manifest.components", None)
    monkeypatch.setitem(sys.modules, "components", None)
    manifest = yaml.safe_load((Path(__file__).parent.parent / "manifest.yaml").read_text())
    resolved = ManifestReferenceResolver().preprocess_manifest(manifest)
    if not hasattr(ConcurrentDeclarativeSource, "_streams_by_name"):
        # Older CDKs build all streams during check, unlike the runtime image.
        resolved["streams"] = [stream for stream in resolved["streams"] if stream["name"] in resolved["check"]["stream_names"]]
        resolved.pop("dynamic_streams", None)
    requests_mock.get(_URL, json={"elements": [{"id": 1}]})
    source = ConcurrentDeclarativeSource(source_config=resolved, config=_CONFIG, custom_components_trusted=False)
    assert source.check(_LOGGER, _CONFIG).status == Status.SUCCEEDED
    assert requests_mock.call_count == 1


def test_check_retries_invalid_url(requests_mock: Any, mocker: Any) -> None:
    mocker.patch("time.sleep", return_value=None)
    requests_mock.get(_URL, [{"exc": requests.exceptions.InvalidURL("DNS failure")}, {"json": {"elements": [{"id": 1}]}}])
    assert get_source(_CONFIG).check(_LOGGER, _CONFIG).status == Status.SUCCEEDED
    assert requests_mock.call_count == 2


def test_accounts_invalid_url_is_transient() -> None:
    accounts = next(stream for stream in get_source(_CONFIG).streams(_CONFIG) if stream.name == "accounts")
    requester = accounts._stream_partition_generator._partition_factory._retriever.requester
    resolution = requester.error_handler.interpret_response(requests.exceptions.InvalidURL("DNS failure"))
    assert resolution.response_action == ResponseAction.RETRY
    assert resolution.failure_type == FailureType.transient_error


@pytest.mark.parametrize("has_accounts", [True, False])
@pytest.mark.parametrize("operation", ["check", "read"])
def test_check_and_read_follow_empty_page(requests_mock: Any, has_accounts: bool, operation: str) -> None:
    requests_mock.get(
        _URL,
        [
            {"json": {"elements": [], "metadata": {"nextPageToken": "next_page"}}},
            {"json": {"elements": [{"id": 1}] if has_accounts else []}},
        ],
    )
    source = get_source(_CONFIG)
    if operation == "check":
        assert source.check(_LOGGER, _CONFIG).status == Status.SUCCEEDED
    else:
        accounts = next(stream for stream in source.streams(_CONFIG) if stream.name == "accounts")
        assert [record.data["id"] for record in run_read(accounts)] == ([1] if has_accounts else [])
