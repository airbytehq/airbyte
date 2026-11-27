# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker

from .report_helpers import (
    mock_missing_report,
    mock_report,
    next_report_cursor,
    previous_report_period,
    report_config,
    report_period,
    report_request,
    report_state,
)
from .response_builder import tabular_response
from .utils import latest_stream_state, read_output


_STREAM_NAME = "subscription_event_report"


class TestSubscriptionEventReportStream(TestCase):
    @HttpMocker()
    def test_read_records_and_emit_state(self, http_mocker: HttpMocker) -> None:
        mock_report(http_mocker, _STREAM_NAME)
        output = read_output(report_config(_STREAM_NAME), _STREAM_NAME, SyncMode.incremental)
        assert output.records[0].record.data["Metric"] == "Downloads"
        assert output.records[0].record.data["report_date"] == report_period(_STREAM_NAME)
        assert latest_stream_state(output, "_sync_cursor") == next_report_cursor(_STREAM_NAME)

    @HttpMocker()
    def test_incremental_sync_uses_prior_state(self, http_mocker: HttpMocker) -> None:
        mock_report(http_mocker, _STREAM_NAME)
        output = read_output(
            report_config(_STREAM_NAME, previous_report_period(_STREAM_NAME)),
            _STREAM_NAME,
            SyncMode.incremental,
            report_state(_STREAM_NAME),
        )
        assert len(output.records) == 1
        assert latest_stream_state(output, "_sync_cursor") == next_report_cursor(_STREAM_NAME)

    @HttpMocker()
    def test_configured_skip_date_requests_sentinel_date(self, http_mocker: HttpMocker) -> None:
        period = report_period(_STREAM_NAME)
        config = report_config(_STREAM_NAME).with_value("subscription_event_skip_dates", [period])
        http_mocker.get(
            report_request(_STREAM_NAME, "2099-01-01").build(),
            tabular_response(_STREAM_NAME),
        )

        output = read_output(config, _STREAM_NAME, SyncMode.incremental)

        assert output.records[0].record.data["report_date"] == period

    @HttpMocker()
    def test_missing_report_is_ignored(self, http_mocker: HttpMocker) -> None:
        mock_missing_report(http_mocker, _STREAM_NAME)
        assert not read_output(report_config(_STREAM_NAME), _STREAM_NAME, SyncMode.incremental).records
