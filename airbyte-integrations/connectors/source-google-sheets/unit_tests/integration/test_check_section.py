#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
"""CHECK through the CDK entrypoint with the `check-section` key of the stepped setup form."""

import pytest

from airbyte_cdk.models import Status
from airbyte_cdk.test.mock_http import HttpMocker

from .conftest import GoogleSheetsBaseTest, oauth_credentials


# The section-aware CHECK lives in the CDK branch of airbytehq/airbyte-python-cdk#1255; until a release ships it, these
# tests skip (they pass against that branch).
pytest.importorskip("airbyte_cdk.sources.utils.check_section", reason="the installed airbyte-cdk has no section-aware CHECK")

_SPREADSHEET_ID = "a_spreadsheet_id"


class TestCheckSection(GoogleSheetsBaseTest):
    @HttpMocker()
    def test_given_spreadsheet_section_when_check_section_then_declared_check_runs_and_succeeds(self, http_mocker: HttpMocker) -> None:
        """A section check of the stepped setup form reads the first sheet with the fields collected so far."""
        GoogleSheetsBaseTest.get_spreadsheet_info_and_sheets(http_mocker, "check_succeeded_meta")
        GoogleSheetsBaseTest.get_sheet_first_row(http_mocker, "check_succeeded_range")
        config = {"check-section": "spreadsheet", "spreadsheet_id": _SPREADSHEET_ID, "credentials": oauth_credentials}

        output = self._check(config, expecting_exception=False)

        assert output.connection_status_messages[-1].connectionStatus.status == Status.SUCCEEDED
        assert output.is_in_logs("Checking configuration section 'spreadsheet'")

    def test_given_spreadsheet_section_without_the_link_when_check_section_then_config_error(self) -> None:
        config = {"check-section": "spreadsheet", "credentials": oauth_credentials}

        output = self._check(config, expecting_exception=False)

        status = output.connection_status_messages[-1].connectionStatus
        assert status.status == Status.FAILED
        assert status.message == "Config validation error: 'spreadsheet_id' is a required property"

    def test_given_review_section_when_check_section_then_rejected_as_it_has_no_check(self) -> None:
        output = self._check({**self._config, "check-section": "review"}, expecting_exception=False)

        status = output.connection_status_messages[-1].connectionStatus
        assert status.status == Status.FAILED
        assert status.message == "Section 'review' has no check: the connector specification does not declare \"check\": true for it."

    def test_given_unknown_section_when_check_section_then_config_error_names_the_sections(self) -> None:
        output = self._check({**self._config, "check-section": "nope"}, expecting_exception=False)

        status = output.connection_status_messages[-1].connectionStatus
        assert status.status == Status.FAILED
        assert status.message == "Unknown check-section 'nope'; the connector specification declares: spreadsheet, review."
