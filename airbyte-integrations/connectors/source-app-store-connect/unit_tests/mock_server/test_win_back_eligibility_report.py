# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from http import HTTPStatus

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker

from .report_helpers import mock_report, next_report_cursor, report_config, report_period
from .response_builder import error_response, tabular_response
from .utils import latest_stream_state, read_output


_STREAM_NAME = "win_back_eligibility_report"


@pytest.mark.parametrize("scenario", ["record", "empty", "missing"])
def test_read_report(scenario: str) -> None:
    with HttpMocker() as http_mocker:
        body = "Subscription Apple ID\tTitle\n" + ("12345\tExample\n" if scenario == "record" else "")
        response = error_response(HTTPStatus.NOT_FOUND) if scenario == "missing" else tabular_response(_STREAM_NAME, body)
        mock_report(http_mocker, _STREAM_NAME, response)
        output = read_output(report_config(_STREAM_NAME), _STREAM_NAME, SyncMode.incremental)
        assert len(output.records) == (1 if scenario == "record" else 0)
        if scenario == "record":
            assert output.records[0].record.data["Subscription Apple ID"] == "12345"
            assert output.records[0].record.data["Title"] == "Example"
            assert output.records[0].record.data["report_date"] == report_period(_STREAM_NAME)
            assert latest_stream_state(output, "_sync_cursor") == next_report_cursor(_STREAM_NAME)
