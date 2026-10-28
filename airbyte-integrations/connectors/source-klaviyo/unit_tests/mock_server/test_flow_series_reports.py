# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, NamedTuple, Optional
from unittest import TestCase

import freezegun
import requests_mock as rm
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import KlaviyoRequestBuilder
from mock_server.response_builder import metrics_response


_NOW = datetime(2024, 2, 1, 12, 0, 0, tzinfo=timezone.utc)
_STREAM_NAME = "flow_series_reports"
_API_KEY = "test_api_key_abc123"
_BASE_URL = "https://a.klaviyo.com/api"

_UNSUPPORTED_METRIC_ID = "unsupported_metric_RJYhz9"
_SUPPORTED_METRIC_ID = "supported_metric_ABC123"


def _days(first_day: datetime, count: int) -> List[str]:
    """Build a `date_times` array of consecutive whole days in the format the API returns."""
    return [(first_day + timedelta(days=offset)).strftime("%Y-%m-%dT00:00:00+00:00") for offset in range(count)]


def _flow_series_success_body(date_times: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Build a successful flow-series-reports response body.

    `date_times` appears once at the attributes level and every statistics array under
    `results` is index-aligned with it. That alignment is what turns one response into one
    record per calendar day.
    """
    date_times = date_times if date_times is not None else _days(datetime(2024, 1, 5, tzinfo=timezone.utc), 3)
    length = len(date_times)
    return {
        "data": {
            "type": "flow-series-report",
            "attributes": {
                "date_times": date_times,
                "results": [
                    {
                        "groupings": {
                            "flow_id": "flow_001",
                            "flow_message_id": "msg_001",
                            "send_channel": "email",
                        },
                        "statistics": {
                            "opens": [10] * length,
                            "clicks": [5] * length,
                            "delivered": [100] * length,
                            "bounced": [2] * length,
                            "recipients": [102] * length,
                        },
                    }
                ],
            },
        },
        "links": {"self": f"{_BASE_URL}/flow-series-reports", "next": None},
    }


def _unsupported_metric_error_body() -> Dict[str, Any]:
    """Build the Klaviyo 400 error body for unsupported conversion metrics."""
    return {
        "errors": [
            {
                "id": "error-id",
                "status": 400,
                "code": "invalid",
                "title": "Bad request",
                "detail": "Passed in conversion metric does not support querying for values data",
            }
        ]
    }


@freezegun.freeze_time(_NOW.isoformat())
class TestFlowSeriesReportsUnsupportedMetric(TestCase):
    """
    Tests for the flow_series_reports stream handling of HTTP 400 errors
    from unsupported conversion metrics.

    The Klaviyo API returns HTTP 400 with "does not support querying for
    values data" for certain conversion metrics. The connector should
    skip these partitions and continue syncing other metrics.
    """

    @HttpMocker()
    def test_ignores_400_unsupported_conversion_metric(self, http_mocker: HttpMocker):
        """
        Verify that when one metric returns the unsupported 400 error,
        the sync continues and returns records from other supported metrics.
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc)).build()

        # Mock the parent metrics_for_reporting stream (GET /metrics)
        http_mocker.get(
            KlaviyoRequestBuilder.metrics_endpoint(_API_KEY).build(),
            metrics_response([_SUPPORTED_METRIC_ID, _UNSUPPORTED_METRIC_ID]),
        )

        # Use the underlying requests_mock to handle POST with dynamic body matching
        def flow_series_callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
            body = json.loads(request.body)
            metric_id = body.get("data", {}).get("attributes", {}).get("conversion_metric_id", "")
            if metric_id == _UNSUPPORTED_METRIC_ID:
                context.status_code = 400
                return json.dumps(_unsupported_metric_error_body())
            context.status_code = 200
            return json.dumps(_flow_series_success_body())

        http_mocker._mocker.post(
            f"{_BASE_URL}/flow-series-reports",
            text=flow_series_callback,
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        # The sync should complete without errors
        assert len(output.errors) == 0, f"Expected no errors but got: {output.errors}"
        # We should have records from the supported metric
        assert len(output.records) >= 1

    @HttpMocker()
    def test_all_metrics_unsupported_yields_zero_records(self, http_mocker: HttpMocker):
        """
        Verify that when all metrics are unsupported, the sync completes
        with zero records and no errors.
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc)).build()

        # Mock the parent metrics_for_reporting stream (GET /metrics)
        http_mocker.get(
            KlaviyoRequestBuilder.metrics_endpoint(_API_KEY).build(),
            metrics_response([_UNSUPPORTED_METRIC_ID]),
        )

        # Every POST returns 400 unsupported
        def all_unsupported_callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
            context.status_code = 400
            return json.dumps(_unsupported_metric_error_body())

        http_mocker._mocker.post(
            f"{_BASE_URL}/flow-series-reports",
            text=all_unsupported_callback,
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.errors) == 0, f"Expected no errors but got: {output.errors}"
        assert len(output.records) == 0


def _timeframe_of(request: rm.request._RequestObjectProxy) -> Dict[str, str]:
    """Read the report timeframe the connector asked for out of the POST body."""
    return json.loads(request.body)["data"]["attributes"]["timeframe"]


def _echo_requested_days_callback(recorded_timeframes: List[Dict[str, str]]):
    """
    Respond the way Klaviyo does: one daily bucket for every calendar day the timeframe
    touches, inclusive of both the first and the last day.
    """

    def callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
        timeframe = _timeframe_of(request)
        recorded_timeframes.append(timeframe)
        first = datetime.fromisoformat(timeframe["start"]).replace(hour=0, minute=0, second=0, microsecond=0)
        last = datetime.fromisoformat(timeframe["end"]).replace(hour=0, minute=0, second=0, microsecond=0)
        context.status_code = 200
        return json.dumps(_flow_series_success_body(_days(first, (last - first).days + 1)))

    return callback


class _Sync(NamedTuple):
    """What one sync asked for, what it produced, and the state a next sync would resume from."""

    timeframes: List[Dict[str, str]]
    records: List[Dict[str, Any]]
    state: Any


def _primary_key_of(record: Dict[str, Any]) -> tuple:
    """The stream's declared primary key, as a destination would compute it for deduplication."""
    return (
        record["date"],
        record["flow_id"],
        record["flow_message_id"],
        record["send_channel"],
        record["conversion_metric_id"],
    )


class TestFlowSeriesReportsPerDayRecords(TestCase):
    """
    The flow-series endpoint returns one shared `date_times` array plus statistics arrays
    aligned to it, so a response describes many calendar days at once. These tests pin the
    resulting record shape and, most importantly, that a day keeps its identity when it is
    read again in a differently sized request window.
    """

    def _read(self, config: Dict[str, Any], state=None):
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        source = get_source(config=config, state=state)
        return read(source, config=config, catalog=catalog, state=state)

    def _read_at(self, now: str, config: Dict[str, Any], state: Optional[Any] = None) -> "_Sync":
        """
        Run one incremental sync at a fixed wall clock, resuming from `state`, against an API that
        reports every calendar day the requested timeframe touches. The returned state is the one
        the sync really emitted, so a following sync can be chained onto it as a connection would.
        """
        input_state = StateBuilder().with_stream_state(_STREAM_NAME, state).build() if state is not None else None
        timeframes: List[Dict[str, str]] = []
        with freezegun.freeze_time(now):
            with HttpMocker() as http_mocker:
                http_mocker.get(
                    KlaviyoRequestBuilder.metrics_endpoint(_API_KEY).build(),
                    metrics_response([_SUPPORTED_METRIC_ID]),
                )
                http_mocker._mocker.post(
                    f"{_BASE_URL}/flow-series-reports",
                    text=_echo_requested_days_callback(timeframes),
                )
                output = self._read(config, state=input_state)

        assert len(output.errors) == 0, f"Expected no errors but got: {output.errors}"
        return _Sync(
            timeframes=timeframes,
            records=[message.record.data for message in output.records],
            state=output.most_recent_state.stream_state,
        )

    def test_emits_one_record_per_day_with_scalar_statistics(self):
        """One response covering three days yields three records, each with scalar statistics."""
        with freezegun.freeze_time("2024-02-10T12:00:00+00:00"):
            config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 2, 1, tzinfo=timezone.utc)).build()
            with HttpMocker() as http_mocker:
                http_mocker.get(
                    KlaviyoRequestBuilder.metrics_endpoint(_API_KEY).build(),
                    metrics_response([_SUPPORTED_METRIC_ID]),
                )
                days = _days(datetime(2024, 2, 1, tzinfo=timezone.utc), 3)
                http_mocker._mocker.post(
                    f"{_BASE_URL}/flow-series-reports",
                    text=lambda request, context: json.dumps(_flow_series_success_body(days)),
                )
                output = self._read(config)

        assert len(output.errors) == 0, f"Expected no errors but got: {output.errors}"
        records = [message.record.data for message in output.records]
        assert len(records) == len(days)
        assert [record["date"] for record in records] == days
        for record in records:
            assert record["statistics"]["opens"] == 10, "statistics must be a scalar for the day, not an array"
            assert record["flow_id"] == "flow_001"
            assert record["conversion_metric_id"] == _SUPPORTED_METRIC_ID

    def test_a_day_reread_in_a_different_window_keeps_the_same_primary_key(self):
        """
        This is the whole point of offering a reporting lookback window: a day re-read on a later
        sync has to come back under the primary key it already had, so a destination that
        deduplicates replaces the row instead of appending a second copy of the same day.

        Two syncs read overlapping periods through differently bounded request windows. The
        earlier sync starts from the configured 2024-01-01 and runs on 2024-02-10, so it asks in
        30 day steps for everything up to the end of 2024-02-09. The later sync resumes from the
        state that sync actually emitted, with a 5 day lookback, and runs on 2024-02-12, so it
        asks for 2024-02-04 to the end of 2024-02-11. The days 2024-02-04 through 2024-02-09 are
        therefore reported twice, inside two windows that share neither a start nor an end.
        """
        earlier = self._read_at(
            "2024-02-10T12:00:00+00:00",
            ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc)).build(),
        )
        later = self._read_at(
            "2024-02-12T12:00:00+00:00",
            ConfigBuilder()
            .with_api_key(_API_KEY)
            .with_start_date(datetime(2024, 1, 1, tzinfo=timezone.utc))
            .with_reporting_lookback_window(5)
            .build(),
            state=earlier.state,
        )

        # The windows must genuinely differ, otherwise the rest of this test proves nothing.
        assert earlier.timeframes and later.timeframes
        assert earlier.timeframes != later.timeframes, "both syncs requested the same window"
        assert min(timeframe["start"] for timeframe in later.timeframes) < max(
            timeframe["end"] for timeframe in earlier.timeframes
        ), f"the later sync re-read nothing: {later.timeframes}"

        earlier_by_day = {record["date"]: _primary_key_of(record) for record in earlier.records}
        later_by_day = {record["date"]: _primary_key_of(record) for record in later.records}

        reread_days = sorted(set(earlier_by_day) & set(later_by_day))
        assert reread_days, (
            "no day was reported by both syncs, so a re-read lands under a brand new identity "
            "and a destination would append duplicates instead of refreshing the day. "
            f"earlier={sorted(earlier_by_day)[-3:]} later={sorted(later_by_day)[:3]}"
        )
        assert reread_days == _days(
            datetime(2024, 2, 4, tzinfo=timezone.utc), 6
        ), f"expected 2024-02-04 through 2024-02-09 to be re-read, got {reread_days}"
        for day in reread_days:
            assert earlier_by_day[day] == later_by_day[day], (
                f"the record for {day} came back under a different primary key, so a destination "
                f"would append a duplicate instead of replacing it: "
                f"{earlier_by_day[day]} != {later_by_day[day]}"
            )
