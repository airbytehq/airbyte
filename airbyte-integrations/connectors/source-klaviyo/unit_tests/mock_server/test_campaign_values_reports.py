# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Dict, List, NamedTuple, Optional
from unittest import TestCase
from unittest.mock import patch

import freezegun
import requests_mock as rm
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import KlaviyoRequestBuilder
from mock_server.response_builder import metrics_response


_STREAM_NAME = "campaign_values_reports"
_API_KEY = "test_api_key_abc123"
_BASE_URL = "https://a.klaviyo.com/api"
_METRIC_ID = "supported_metric_ABC123"
# One 30 day step covers everything from here to the frozen clocks below, so every sync in this
# module makes a single report request. The endpoint is budgeted at 2 calls per minute, so extra
# requests cost about a minute of test runtime each.
_START_DATE = datetime(2024, 6, 1, tzinfo=timezone.utc)
_MIDNIGHT = time(0, 0, 0)


def _campaign_values_body() -> Dict[str, Any]:
    """
    A campaign-values response: one aggregate row per grouping for the whole requested period.

    Unlike flow-series there is no `date_times` array and no per-day breakdown, which is why the
    connector has to take the record's `date` from the requested period rather than the payload.
    """
    return {
        "data": {
            "type": "campaign-values-report",
            "attributes": {
                "results": [
                    {
                        "groupings": {
                            "campaign_id": "campaign_001",
                            "campaign_message_id": "msg_001",
                            "send_channel": "email",
                        },
                        "statistics": {"opens": 10, "clicks": 5, "delivered": 100, "recipients": 102},
                    }
                ]
            },
        },
        "links": {"self": f"{_BASE_URL}/campaign-values-reports", "next": None},
    }


def _recording_callback(recorded_timeframes: List[Dict[str, str]]):
    """Record the timeframe of every report request and answer them all the same way."""

    def callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
        recorded_timeframes.append(json.loads(request.body)["data"]["attributes"]["timeframe"])
        context.status_code = 200
        return json.dumps(_campaign_values_body())

    return callback


def _time_of(timestamp: str) -> time:
    """The time of day a report timestamp carries, whatever offset notation it uses."""
    return datetime.fromisoformat(timestamp).time()


def _days_covered(timeframes: List[Dict[str, str]]) -> List[date]:
    """
    Every calendar day the given timeframes ask Klaviyo to report on, repeats included.

    Report timeframes are inclusive of both ends and Klaviyo rounds the end up to :59:59 of the
    hour it falls in, so the day the end lands on is always part of the answer whatever time it
    carries.
    """
    days: List[date] = []
    for timeframe in timeframes:
        first = datetime.fromisoformat(timeframe["start"]).date()
        last = datetime.fromisoformat(timeframe["end"]).date()
        days.extend(first + timedelta(days=offset) for offset in range((last - first).days + 1))
    return days


def _cursor_values(state: Any) -> List[str]:
    """Every cursor value held in a per-partition state blob, the global fallback included."""
    blob = state if isinstance(state, dict) else state.__dict__
    values = [per_partition["cursor"]["date"] for per_partition in blob.get("states") or []]
    global_cursor = (blob.get("state") or {}).get("date")
    if global_cursor:
        values.append(global_cursor)
    return values


class _Sync(NamedTuple):
    """What one sync asked for, what it produced, and the state a next sync would resume from."""

    timeframes: List[Dict[str, str]]
    records: List[Dict[str, Any]]
    state: Any


def _read_at(now: str, config: Dict[str, Any], state: Optional[Any] = None) -> _Sync:
    """Run one incremental sync at a fixed wall clock, resuming from `state` if one is given."""
    input_state = StateBuilder().with_stream_state(_STREAM_NAME, state).build() if state is not None else None
    timeframes: List[Dict[str, str]] = []
    with freezegun.freeze_time(now):
        with HttpMocker() as http_mocker:
            http_mocker.get(
                KlaviyoRequestBuilder.metrics_endpoint(_API_KEY).build(),
                metrics_response([_METRIC_ID]),
            )
            http_mocker._mocker.post(
                f"{_BASE_URL}/campaign-values-reports",
                text=_recording_callback(timeframes),
            )
            catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
            source = get_source(config=config, state=input_state)
            output = read(source, config=config, catalog=catalog, state=input_state)

    assert len(output.errors) == 0, f"Expected no errors but got: {output.errors}"
    return _Sync(
        timeframes=timeframes,
        records=[message.record.data for message in output.records],
        state=output.most_recent_state.stream_state,
    )


def _config(**overrides: Any) -> Dict[str, Any]:
    return ConfigBuilder().with_api_key(_API_KEY).with_start_date(_START_DATE).build() | overrides


class TestCampaignValuesReportsWindows(TestCase):
    """
    The campaign-values endpoint answers with one aggregate per requested period, so the period a
    sync asks for is both the record's identity and the cursor it leaves behind. These tests drive
    the real cursor across a state round trip - sync 2 resumes from the state sync 1 actually
    emitted, not from a hand-written one - because an overlap between the two silently
    double-counts every shared day: the same day ends up inside two aggregates filed under two
    different `date` values, which no destination can deduplicate.
    """

    def test_a_resumed_sync_starts_where_the_previous_one_stopped(self):
        """
        A sync that runs at 12:34:56 must not leave the wall clock behind as its cursor. The
        cursor is where the next sync starts asking, so a mid-day value makes the next sync
        request a period that begins in the middle of a day already reported.
        """
        first = _read_at("2024-06-15T12:34:56+00:00", _config())
        second = _read_at("2024-06-20T08:15:00+00:00", _config(), state=first.state)

        assert first.timeframes and second.timeframes, f"a sync requested nothing: {first.timeframes} {second.timeframes}"
        for cursor_value in _cursor_values(first.state):
            assert _time_of(cursor_value) == _MIDNIGHT, f"the stored cursor is a wall-clock instant: {cursor_value}"
        for record in first.records + second.records:
            assert _time_of(record["date"]) == _MIDNIGHT, f"record date is a wall-clock instant: {record['date']}"
        for timeframe in second.timeframes:
            assert _time_of(timeframe["start"]) == _MIDNIGHT, f"the resumed sync starts requesting mid-day: {timeframe}"

        first_days, second_days = set(_days_covered(first.timeframes)), set(_days_covered(second.timeframes))
        assert not first_days & second_days, (
            f"both syncs reported {sorted(first_days & second_days)}, so those days land in two aggregates "
            f"under two different `date` values: {first.timeframes[-1]} then {second.timeframes[0]}"
        )
        assert min(second_days) == max(first_days) + timedelta(days=1), (
            f"nothing reports the days between {max(first_days)} and {min(second_days)}: "
            f"{first.timeframes[-1]} then {second.timeframes[0]}"
        )
        assert max(second_days) == date(2024, 6, 19), f"the sync reached past the last complete day: {second.timeframes[-1]}"

    def test_a_second_sync_on_the_same_day_requests_nothing(self):
        """
        No further day has completed since the previous sync ran, so there is nothing to ask for.
        A rerun that did request something would re-aggregate days already written.
        """
        first = _read_at("2024-06-15T12:34:56+00:00", _config())
        rerun = _read_at("2024-06-15T21:00:00+00:00", _config(), state=first.state)

        assert rerun.timeframes == [], f"the rerun re-requested reporting periods: {rerun.timeframes}"
        assert rerun.records == []
        assert _cursor_values(rerun.state) == _cursor_values(first.state), "the rerun moved the cursor without reading anything"


@freezegun.freeze_time("2024-06-15T12:34:56+00:00")
class TestCampaignValuesReportsRecords(TestCase):
    """The shape the aggregate rows arrive in."""

    @HttpMocker()
    def test_flattens_results_and_adds_the_grouping_fields(self, http_mocker: HttpMocker):
        config = _config()
        http_mocker.get(KlaviyoRequestBuilder.metrics_endpoint(_API_KEY).build(), metrics_response([_METRIC_ID]))
        http_mocker._mocker.post(
            f"{_BASE_URL}/campaign-values-reports",
            text=lambda request, context: json.dumps(_campaign_values_body()),
        )

        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(get_source(config=config), config=config, catalog=catalog)

        assert len(output.errors) == 0, f"Expected no errors but got: {output.errors}"
        record = output.records[0].record.data
        assert record["campaign_id"] == "campaign_001"
        assert record["campaign_message_id"] == "msg_001"
        assert record["send_channel"] == "email"
        assert record["conversion_metric_id"] == _METRIC_ID
        assert record["statistics"]["opens"] == 10
        # The period ran to the end of 2024-06-14, and `date` is the midnight that closes it, so
        # the row says "everything up to, and not including, 2024-06-15".
        assert record["date"] == "2024-06-15T00:00:00+00:00"

    @HttpMocker()
    def test_daily_quota_retry_after_fails_fast(self, http_mocker: HttpMocker):
        config = _config()
        http_mocker.get(KlaviyoRequestBuilder.metrics_endpoint(_API_KEY).build(), metrics_response([_METRIC_ID]))
        report_request = HttpRequest(
            f"{_BASE_URL}/campaign-values-reports",
            body={
                "data": {
                    "type": "campaign-values-report",
                    "attributes": {
                        "statistics": [
                            "average_order_value",
                            "bounce_rate",
                            "bounced",
                            "bounced_or_failed",
                            "bounced_or_failed_rate",
                            "click_rate",
                            "click_to_open_rate",
                            "clicks",
                            "clicks_unique",
                            "conversion_rate",
                            "conversion_uniques",
                            "conversion_value",
                            "conversions",
                            "delivered",
                            "delivery_rate",
                            "failed",
                            "failed_rate",
                            "message_segment_count_sum",
                            "open_rate",
                            "opens",
                            "opens_unique",
                            "recipients",
                            "revenue_per_recipient",
                            "spam_complaint_rate",
                            "spam_complaints",
                            "text_message_credit_usage_amount",
                            "text_message_roi",
                            "text_message_spend",
                            "unsubscribe_rate",
                            "unsubscribe_uniques",
                            "unsubscribes",
                        ],
                        "timeframe": {
                            "start": "2024-06-01T00:00:00+0000",
                            "end": "2024-06-14T23:59:59+0000",
                        },
                        "conversion_metric_id": _METRIC_ID,
                    },
                }
            },
        )
        http_mocker.post(
            report_request,
            HttpResponse(
                json.dumps({"errors": [{"detail": "Rate limit exceeded"}]}),
                429,
                {"Retry-After": "73473"},
            ),
        )

        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        with (
            patch("airbyte_cdk.sources.streams.http.rate_limiting.time") as rate_limiting_time,
            patch("airbyte_cdk.sources.streams.call_rate.time") as call_rate_time,
        ):
            output = read(get_source(config=config), config=config, catalog=catalog)

        assert output.records == []
        assert output.errors
        assert "greater than max waiting time" in output.get_formatted_error_message()
        rate_limiting_time.sleep.assert_not_called()
        call_rate_time.sleep.assert_not_called()
        http_mocker.assert_number_of_calls(report_request, 1)
