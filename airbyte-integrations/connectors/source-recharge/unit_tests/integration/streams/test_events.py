#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from datetime import timedelta
from unittest import TestCase

import freezegun

from airbyte_cdk.test.mock_http import HttpMocker

from ..config import DATE_TIME_FORMAT, NOW
from ..response_builder import NEXT_PAGE_TOKEN, get_stream_record, get_stream_response
from ..utils import StreamTestCase, config, get_cursor_value_from_state_message, read_full_refresh, read_incremental


_STREAM_NAME = "events"
_CURSOR_FIELD = "created_at"

# The events endpoint rejects created_at_min older than 7 days ("created_at_min
# must be less than 7 days ago"), unlike every other stream. start_datetime's
# min_datetime floors the evaluated date at NOW - 7 days, so any start_date
# older than that (as START_DATE, 2023-01-01, always is relative to NOW) is
# clamped to this value rather than sent as-is. See manifest.yaml.
_CLAMPED_CREATED_MIN = (NOW - timedelta(days=7)).strftime(DATE_TIME_FORMAT)

# Record cursor values used by the TestIncremental cases below. These must
# fall within the slice window (created_at_min .. now), which min_datetime
# now floors at NOW - 7 days -- a fixed date like 2024-01-01 would be earlier
# than that floor and get silently dropped by the cursor as out-of-range
# (DatetimeBasedCursor.observe()'s _is_within_daterange_boundaries check),
# producing no state at all rather than a wrong one.
_RECENT_MIN_CURSOR_VALUE = (NOW - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
_RECENT_MAX_CURSOR_VALUE = (NOW - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S+00:00")


@freezegun.freeze_time(NOW.isoformat())
class TestFullRefresh(StreamTestCase):
    _STREAM_NAME = "events"

    @HttpMocker()
    def test_given_one_page_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        req = self.stream_request().with_limit(250).with_created_min(_CLAMPED_CREATED_MIN).build()
        http_mocker.get(
            req,
            get_stream_response(_STREAM_NAME).with_record(get_stream_record(_STREAM_NAME, "id", _CURSOR_FIELD)).build(),
        )
        output = read_full_refresh(self._config, _STREAM_NAME)
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_multiple_pages_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            self.stream_request().with_limit(250).with_next_page_token(NEXT_PAGE_TOKEN).build(),
            get_stream_response(_STREAM_NAME).with_record(get_stream_record(_STREAM_NAME, "id", _CURSOR_FIELD)).build(),
        )
        http_mocker.get(
            self.stream_request().with_limit(250).with_created_min(_CLAMPED_CREATED_MIN).build(),
            get_stream_response(_STREAM_NAME).with_pagination().with_record(get_stream_record(_STREAM_NAME, "id", _CURSOR_FIELD)).build(),
        )

        output = read_full_refresh(self._config, _STREAM_NAME)
        assert len(output.records) == 2

    @HttpMocker()
    def test_given_recent_start_date_when_read_then_created_min_is_not_clamped(self, http_mocker: HttpMocker) -> None:
        # A start_date already inside the 7-day window must be sent as-is --
        # min_datetime should only ever push an older date forward, never
        # move a recent one further back.
        recent_start_date = (NOW - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        recent_config = config().with_access_token(self._access_token).with_start_date(recent_start_date)

        expected_created_min = (NOW - timedelta(days=2)).strftime(DATE_TIME_FORMAT)
        req = self.stream_request().with_limit(250).with_created_min(expected_created_min).build()
        http_mocker.get(
            req,
            get_stream_response(_STREAM_NAME).with_record(get_stream_record(_STREAM_NAME, "id", _CURSOR_FIELD)).build(),
        )

        output = read_full_refresh(recent_config, _STREAM_NAME)
        assert len(output.records) == 1


@freezegun.freeze_time(NOW.isoformat())
class TestIncremental(StreamTestCase):
    _STREAM_NAME = "events"

    @HttpMocker()
    def test_state_message_produced_while_read_and_state_match_latest_record(self, http_mocker: HttpMocker) -> None:
        min_cursor_value = _RECENT_MIN_CURSOR_VALUE
        max_cursor_value = _RECENT_MAX_CURSOR_VALUE

        http_mocker.get(
            self.stream_request().with_limit(250).with_created_min(_CLAMPED_CREATED_MIN).build(),
            get_stream_response(_STREAM_NAME)
            .with_record(get_stream_record(_STREAM_NAME, "id", _CURSOR_FIELD).with_cursor(min_cursor_value))
            .with_record(get_stream_record(_STREAM_NAME, "id", _CURSOR_FIELD).with_cursor(max_cursor_value))
            .build(),
        )

        output = read_incremental(self._config, _STREAM_NAME)
        test_cursor_value = get_cursor_value_from_state_message(output, _CURSOR_FIELD)
        assert test_cursor_value == max_cursor_value

    @HttpMocker()
    def test_given_multiple_pages_when_read_then_return_records_with_state(self, http_mocker: HttpMocker) -> None:
        min_cursor_value = _RECENT_MIN_CURSOR_VALUE
        max_cursor_value = _RECENT_MAX_CURSOR_VALUE
        http_mocker.get(
            self.stream_request().with_limit(250).with_next_page_token(NEXT_PAGE_TOKEN).build(),
            get_stream_response(_STREAM_NAME).with_record(get_stream_record(_STREAM_NAME, "id", _CURSOR_FIELD)).build(),
        )
        http_mocker.get(
            self.stream_request().with_limit(250).with_created_min(_CLAMPED_CREATED_MIN).build(),
            get_stream_response(_STREAM_NAME)
            .with_pagination()
            .with_record(get_stream_record(_STREAM_NAME, "id", _CURSOR_FIELD).with_cursor(min_cursor_value))
            .with_record(get_stream_record(_STREAM_NAME, "id", _CURSOR_FIELD).with_cursor(max_cursor_value))
            .build(),
        )

        output = read_incremental(self._config, _STREAM_NAME)
        assert len(output.records) == 3
