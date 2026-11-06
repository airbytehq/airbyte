#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
"""CHECK through the CDK entrypoint with the `check-section` key of the stepped setup form."""

import json
import logging

import pytest
from airbyte_protocol_dataclasses.models import Status

from airbyte_cdk import AirbyteEntrypoint
from airbyte_cdk.models import Type

from .conftest import get_source


# The section-aware CHECK lives in the CDK branch of airbytehq/airbyte-python-cdk#1255; until a release ships it, these
# tests skip (they pass against that branch).
pytest.importorskip("airbyte_cdk.sources.utils.check_section", reason="the installed airbyte-cdk has no section-aware CHECK")


ACCOUNTS_URL = "https://api.linkedin.com/rest/adAccounts?q=search&pageSize=500"

ACCOUNT_SECTION_CONFIG = {
    "check-section": "account",
    "start_date": "2021-01-01",
    "credentials": {"auth_method": "access_token", "access_token": "access_token"},
}

FULL_CONFIG = {
    "start_date": "2021-01-01",
    "credentials": {"auth_method": "access_token", "access_token": "access_token"},
    "account_ids": [1, 2],
    "lookback_window": 3,
    "num_workers": 5,
}

logger = logging.getLogger("airbyte")


@pytest.fixture(autouse=True)
def no_sleep(mocker):
    mocker.patch("time.sleep", lambda x: None)


def _run_check(tmp_path, config):
    """Runs `check` end to end through the CDK entrypoint and returns the (status, message) of the CONNECTION_STATUS message."""
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))
    entrypoint = AirbyteEntrypoint(get_source(config))
    messages = [json.loads(line) for line in entrypoint.run(entrypoint.parse_args(["check", "--config", str(config_path)]))]
    statuses = [message["connectionStatus"] for message in messages if message["type"] == Type.CONNECTION_STATUS.value]
    assert len(statuses) == 1, messages
    return statuses[0]["status"], statuses[0].get("message")


def test_check_section_of_the_account_section_reads_the_accounts(requests_mock):
    """The declarative check reads the accounts stream with the configuration collected so far."""
    accounts = requests_mock.get(ACCOUNTS_URL, json={"elements": [{"id": 1}]})
    config = {key: value for key, value in ACCOUNT_SECTION_CONFIG.items() if key != "check-section"}

    status = get_source(config).check_section(logger, "account", config)

    assert status.status is Status.SUCCEEDED
    assert accounts.called_once


def test_check_of_the_account_section_succeeds(tmp_path, requests_mock):
    accounts = requests_mock.get(ACCOUNTS_URL, json={"elements": [{"id": 1}]})

    assert _run_check(tmp_path, ACCOUNT_SECTION_CONFIG) == (Status.SUCCEEDED.value, None)
    assert accounts.called_once


def test_check_of_the_account_section_fails_on_a_rejected_token(tmp_path, requests_mock):
    requests_mock.get(ACCOUNTS_URL, status_code=403, json={})

    status, message = _run_check(tmp_path, ACCOUNT_SECTION_CONFIG)

    assert status == Status.FAILED.value
    assert "Stream accounts is not available: HTTP Status Code: 403" in message


def test_check_of_the_account_section_requires_its_fields(tmp_path, requests_mock):
    accounts = requests_mock.get(ACCOUNTS_URL, json={"elements": [{"id": 1}]})
    config = {key: value for key, value in ACCOUNT_SECTION_CONFIG.items() if key != "start_date"}

    assert _run_check(tmp_path, config) == (Status.FAILED.value, "Config validation error: 'start_date' is a required property")
    assert not accounts.called


def test_check_of_the_account_section_still_validates_the_present_fields(tmp_path, requests_mock):
    accounts = requests_mock.get(ACCOUNTS_URL, json={"elements": [{"id": 1}]})
    config = {**ACCOUNT_SECTION_CONFIG, "start_date": "01/01/2021"}

    status, message = _run_check(tmp_path, config)

    assert status == Status.FAILED.value
    assert message.startswith("Config validation error: ")
    assert not accounts.called


def test_check_of_an_unknown_section_fails(tmp_path, requests_mock):
    accounts = requests_mock.get(ACCOUNTS_URL, json={"elements": [{"id": 1}]})

    assert _run_check(tmp_path, {**ACCOUNT_SECTION_CONFIG, "check-section": "nope"}) == (
        Status.FAILED.value,
        "Unknown check-section 'nope'; the connector specification declares: account, review.",
    )
    assert not accounts.called


def test_check_of_the_review_section_is_rejected_as_it_has_no_check(tmp_path, requests_mock):
    accounts = requests_mock.get(ACCOUNTS_URL, json={"elements": [{"id": 1}]})

    assert _run_check(tmp_path, {**FULL_CONFIG, "check-section": "review"}) == (
        Status.FAILED.value,
        "Section 'review' has no check: the connector specification does not declare \"check\": true for it.",
    )
    assert not accounts.called


def test_check_without_the_key_validates_the_full_spec(tmp_path, requests_mock):
    accounts = requests_mock.get(ACCOUNTS_URL, json={"elements": [{"id": 1}]})
    config = {key: value for key, value in FULL_CONFIG.items() if key != "start_date"}

    assert _run_check(tmp_path, config) == (Status.FAILED.value, "Config validation error: 'start_date' is a required property")
    assert not accounts.called


def test_check_without_the_key_succeeds_with_the_full_config(tmp_path, requests_mock):
    accounts = requests_mock.get(ACCOUNTS_URL, json={"elements": [{"id": 1}]})

    assert _run_check(tmp_path, FULL_CONFIG) == (Status.SUCCEEDED.value, None)
    assert accounts.called_once
