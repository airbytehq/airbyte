# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from typing import Any

import pytest
import requests

from airbyte_cdk.models import FailureType, Status
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
    _assert_check_failure(config, "no access to any ad account")
    assert "Campaign Manager" in get_source(config).check(_LOGGER, config).message


def test_check_accessible_accounts(requests_mock: Any) -> None:
    requests_mock.get(_URL, json={"elements": [{"id": 1}]})
    assert get_source(_CONFIG).check(_LOGGER, _CONFIG).status == Status.SUCCEEDED


def test_accounts_extractor_allows_empty_final_page(components_module: Any, requests_mock: Any) -> None:
    requests_mock.get(_URL, [{"json": {"elements": [{"id": 1}]}}, {"json": {"elements": []}}])
    extractor = components_module.LinkedInAdsAccountsExtractor()
    assert list(extractor.extract_records(requests.get(_URL))) == [{"id": 1}]
    assert list(extractor.extract_records(requests.get(_URL))) == []


@pytest.mark.parametrize("has_accounts", [True, False])
def test_check_follows_empty_page(requests_mock: Any, has_accounts: bool) -> None:
    requests_mock.get(
        _URL,
        [
            {"json": {"elements": [], "metadata": {"nextPageToken": "next_page"}}},
            {"json": {"elements": [{"id": 1}] if has_accounts else []}},
        ],
    )
    if has_accounts:
        assert get_source(_CONFIG).check(_LOGGER, _CONFIG).status == Status.SUCCEEDED
    else:
        _assert_check_failure(_CONFIG, "no access to any ad account")
