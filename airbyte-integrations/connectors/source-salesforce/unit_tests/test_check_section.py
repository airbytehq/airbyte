#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
"""The section-aware CHECK of the stepped setup form: `check_section_connection` and `check` with the `check-section` key."""

import json
import logging

import pytest
import requests_mock
from config_builder import ConfigBuilder
from source_salesforce.api import API_VERSION
from source_salesforce.source import SourceSalesforce

from airbyte_cdk import AirbyteEntrypoint
from airbyte_cdk.models import FailureType, Status, Type
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


LOGIN_URL = "https://login.salesforce.com/services/oauth2/token"
INSTANCE_URL = "https://instance.salesforce.com"
SOBJECTS_URL = f"{INSTANCE_URL}/services/data/{API_VERSION}/sobjects"

ACCOUNT_SECTION_CONFIG = {
    "check-section": "account",
    "is_sandbox": False,
    "client_id": "fake_client_id",
    "client_secret": "fake_client_secret",
    "refresh_token": "fake_refresh_token",
}

logger = logging.getLogger("airbyte")


def _given_login(mocker: requests_mock.Mocker):
    return mocker.post(LOGIN_URL, json={"access_token": "fake_access_token", "instance_url": INSTANCE_URL})


def _given_rejected_login(mocker: requests_mock.Mocker):
    return mocker.post(LOGIN_URL, status_code=400, json={"error": "invalid_grant", "error_description": "expired access/refresh token"})


def _given_describe(mocker: requests_mock.Mocker):
    return mocker.get(SOBJECTS_URL, json={"sobjects": [{"name": "Account", "queryable": True}]})


class TestCheckSectionConnection:
    def test_account_section_logs_in_and_describes_the_objects(self):
        config = {key: value for key, value in ACCOUNT_SECTION_CONFIG.items() if key != "check-section"}
        source = SourceSalesforce(None, config, None)

        with requests_mock.Mocker() as mocker:
            _given_login(mocker)
            describe = _given_describe(mocker)

            assert source.check_section_connection(logger, "account", config) == (True, None)

        assert describe.called_once

    def test_account_section_reports_a_rejected_login(self):
        config = {key: value for key, value in ACCOUNT_SECTION_CONFIG.items() if key != "check-section"}
        source = SourceSalesforce(None, config, None)

        with requests_mock.Mocker() as mocker:
            _given_rejected_login(mocker)
            with pytest.raises(AirbyteTracedException) as exc_info:
                source.check_section_connection(logger, "account", config)

        assert exc_info.value.message == "The authentication to SalesForce has expired. Re-authenticate to restore access to SalesForce."

    def test_account_section_validates_the_data_filters(self):
        config = ConfigBuilder().build()
        config = {**config, "start_date": "2021-07-26T00:00:00Z", "end_date": "2021-07-25T00:00:00Z"}
        source = SourceSalesforce(None, config, None)

        with pytest.raises(AirbyteTracedException) as exc_info:
            source.check_section_connection(logger, "account", config)

        assert exc_info.value.failure_type == FailureType.config_error
        assert "must be later than 'Start Date'" in exc_info.value.message

    def test_unknown_section_is_a_config_error(self):
        config = ConfigBuilder().build()
        source = SourceSalesforce(None, config, None)

        with requests_mock.Mocker() as mocker:
            login = _given_login(mocker)
            with pytest.raises(AirbyteTracedException) as exc_info:
                source.check_section_connection(logger, "review", config)

        assert exc_info.value.failure_type == FailureType.config_error
        assert exc_info.value.message == "Section 'review' has no section check."
        assert not login.called


def _run_check(tmp_path, config):
    """Runs `check` end to end through the CDK entrypoint and returns the (status, message) of the CONNECTION_STATUS message."""
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))
    entrypoint = AirbyteEntrypoint(SourceSalesforce(None, config, None))
    messages = [json.loads(line) for line in entrypoint.run(entrypoint.parse_args(["check", "--config", str(config_path)]))]
    statuses = [message["connectionStatus"] for message in messages if message["type"] == Type.CONNECTION_STATUS.value]
    assert len(statuses) == 1, messages
    return statuses[0]["status"], statuses[0].get("message")


class TestCheckEntrypoint:
    def test_account_section_succeeds(self, tmp_path):
        with requests_mock.Mocker() as mocker:
            _given_login(mocker)
            describe = _given_describe(mocker)

            assert _run_check(tmp_path, ACCOUNT_SECTION_CONFIG) == (Status.SUCCEEDED.value, None)

        assert describe.called_once

    def test_account_section_fails_on_a_rejected_login(self, tmp_path):
        with requests_mock.Mocker() as mocker:
            _given_rejected_login(mocker)

            assert _run_check(tmp_path, ACCOUNT_SECTION_CONFIG) == (
                Status.FAILED.value,
                "The authentication to SalesForce has expired. Re-authenticate to restore access to SalesForce.",
            )

    def test_account_section_requires_its_fields(self, tmp_path):
        config = {key: value for key, value in ACCOUNT_SECTION_CONFIG.items() if key != "refresh_token"}

        with requests_mock.Mocker() as mocker:
            login = _given_login(mocker)

            assert _run_check(tmp_path, config) == (Status.FAILED.value, "Config validation error: 'refresh_token' is a required property")

        assert not login.called

    def test_account_section_still_validates_the_present_fields(self, tmp_path):
        config = {**ACCOUNT_SECTION_CONFIG, "start_date": "yesterday"}

        with requests_mock.Mocker() as mocker:
            login = _given_login(mocker)
            status, message = _run_check(tmp_path, config)

        assert status == Status.FAILED.value
        assert message.startswith("Config validation error: ")
        assert not login.called

    def test_unknown_section_fails(self, tmp_path):
        with requests_mock.Mocker() as mocker:
            login = _given_login(mocker)

            assert _run_check(tmp_path, {**ACCOUNT_SECTION_CONFIG, "check-section": "nope"}) == (
                Status.FAILED.value,
                "Unknown check-section 'nope'; the connector specification declares: account, review.",
            )

        assert not login.called

    def test_review_section_is_rejected_as_it_has_no_check(self, tmp_path):
        with requests_mock.Mocker() as mocker:
            login = _given_login(mocker)

            assert _run_check(tmp_path, {**ACCOUNT_SECTION_CONFIG, "check-section": "review"}) == (
                Status.FAILED.value,
                "Section 'review' has no check: the connector specification does not declare \"check\": true for it.",
            )

        assert not login.called

    def test_without_the_key_the_full_spec_is_validated(self, tmp_path):
        config = {key: value for key, value in ACCOUNT_SECTION_CONFIG.items() if key not in ("check-section", "client_id")}

        with requests_mock.Mocker() as mocker:
            login = _given_login(mocker)

            assert _run_check(tmp_path, config) == (Status.FAILED.value, "Config validation error: 'client_id' is a required property")

        assert not login.called

    def test_without_the_key_the_full_config_succeeds(self, tmp_path):
        config = {**ConfigBuilder().build(), "lookback_window": "PT30M", "stream_slice_step": "P7D"}

        with requests_mock.Mocker() as mocker:
            _given_login(mocker)
            describe = _given_describe(mocker)

            assert _run_check(tmp_path, config) == (Status.SUCCEEDED.value, None)

        assert describe.called_once
