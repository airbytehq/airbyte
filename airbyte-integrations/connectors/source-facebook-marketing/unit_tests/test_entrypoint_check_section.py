#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
"""CHECK through the CDK entrypoint with the `check-section` key of the stepped setup form."""

import json

import pytest
from facebook_business import FacebookAdsApi, FacebookSession
from source_facebook_marketing import SourceFacebookMarketing

from airbyte_cdk import AirbyteEntrypoint
from airbyte_cdk.models import Status, Type


ACCOUNT_URL = FacebookSession.GRAPH + f"/{FacebookAdsApi.API_VERSION}/act_123/"

ACCOUNT_SECTION_CONFIG = {
    "check-section": "account",
    "account_ids": ["123"],
    "credentials": {"auth_type": "Service", "access_token": "ACCESS_TOKEN"},
}

FULL_CONFIG = {
    "account_ids": ["123"],
    "credentials": {"auth_type": "Service", "access_token": "ACCESS_TOKEN"},
    "start_date": "2019-10-10T00:00:00Z",
    "end_date": "2020-10-10T00:00:00Z",
    "page_size": 50,
    "insights_lookback_window": 7,
    "insights_job_timeout": 30,
}


@pytest.fixture(name="account_request")
def account_request_fixture(requests_mock):
    return requests_mock.register_uri("GET", ACCOUNT_URL, json={"account_id": "123", "timezone_name": "UTC"})


def _run_check(tmp_path, config):
    """Runs `check` end to end and returns the (status, message) of the CONNECTION_STATUS message."""
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))
    entrypoint = AirbyteEntrypoint(SourceFacebookMarketing())
    messages = [json.loads(line) for line in entrypoint.run(entrypoint.parse_args(["check", "--config", str(config_path)]))]
    statuses = [message["connectionStatus"] for message in messages if message["type"] == Type.CONNECTION_STATUS.value]
    assert len(statuses) == 1, messages
    return statuses[0]["status"], statuses[0].get("message")


def test_check_of_the_account_section_reaches_the_ad_account_and_succeeds(tmp_path, account_request):
    assert _run_check(tmp_path, ACCOUNT_SECTION_CONFIG) == (Status.SUCCEEDED.value, None)
    assert account_request.called_once


def test_check_of_the_account_section_fails_on_a_rejected_token(tmp_path, requests_mock):
    requests_mock.register_uri(
        "GET",
        ACCOUNT_URL,
        status_code=400,
        json={"error": {"message": "Invalid OAuth access token.", "type": "OAuthException", "code": 190}},
    )

    status, message = _run_check(tmp_path, ACCOUNT_SECTION_CONFIG)

    assert status == Status.FAILED.value
    assert "The access token for this connection is invalid or corrupted." in message


def test_check_of_the_account_section_requires_its_fields(tmp_path, account_request):
    config = {key: value for key, value in ACCOUNT_SECTION_CONFIG.items() if key != "credentials"}

    assert _run_check(tmp_path, config) == (Status.FAILED.value, "Config validation error: 'credentials' is a required property")
    assert not account_request.called


def test_check_of_the_account_section_still_validates_the_present_fields(tmp_path, account_request):
    config = {**ACCOUNT_SECTION_CONFIG, "account_ids": ["act_123"]}

    status, message = _run_check(tmp_path, config)

    assert status == Status.FAILED.value
    assert message.startswith("Config validation error: ")
    assert not account_request.called


def test_check_of_an_unknown_section_fails(tmp_path, account_request):
    assert _run_check(tmp_path, {**ACCOUNT_SECTION_CONFIG, "check-section": "nope"}) == (
        Status.FAILED.value,
        "Unknown check-section 'nope'; the connector specification declares: account, review.",
    )
    assert not account_request.called


def test_check_of_the_review_section_is_rejected_as_it_has_no_check(tmp_path, account_request):
    assert _run_check(tmp_path, {**FULL_CONFIG, "check-section": "review"}) == (
        Status.FAILED.value,
        "Section 'review' has no check: the connector specification does not declare \"check\": true for it.",
    )
    assert not account_request.called


def test_check_without_the_key_validates_the_full_spec(tmp_path, account_request):
    config = {key: value for key, value in FULL_CONFIG.items() if key != "account_ids"}

    assert _run_check(tmp_path, config) == (Status.FAILED.value, "Config validation error: 'account_ids' is a required property")
    assert not account_request.called


def test_check_without_the_key_succeeds_with_the_full_config(tmp_path, account_request):
    assert _run_check(tmp_path, FULL_CONFIG) == (Status.SUCCEEDED.value, None)
    assert account_request.called_once
