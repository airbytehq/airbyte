#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from unittest import TestCase

import freezegun

from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder

from ..config import NOW, START_DATE
from ..response_builder import NEXT_PAGE_TOKEN, get_stream_record, get_stream_response
from ..utils import StreamTestCase, config, get_cursor_value_from_state_message, read_full_refresh, read_incremental


_STREAM_NAME = "discounts"
_CURSOR_FIELD = "updated_at"


@freezegun.freeze_time(NOW.isoformat())
class TestFullRefresh(StreamTestCase):
    _STREAM_NAME = "discounts"

    @HttpMocker()
    def test_given_one_page_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            self.stream_request().with_limit(250).with_updated_at_min(START_DATE).build(),
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
            self.stream_request().with_limit(250).with_updated_at_min(START_DATE).build(),
            get_stream_response(_STREAM_NAME).with_pagination().with_record(get_stream_record(_STREAM_NAME, "id", _CURSOR_FIELD)).build(),
        )

        output = read_full_refresh(self._config, _STREAM_NAME)
        assert len(output.records) == 2


@freezegun.freeze_time(NOW.isoformat())
class TestIncremental(StreamTestCase):
    _STREAM_NAME = "discounts"

    @HttpMocker()
    def test_given_legacy_state_and_lookback_when_read_then_resume_lookback_days_before_state(self, http_mocker: HttpMocker) -> None:
        state = StateBuilder().with_stream_state(_STREAM_NAME, {_CURSOR_FIELD: "2024-02-01T00:00:00+00:00"}).build()
        request = self.stream_request().with_limit(250).with_updated_at_min("2024-01-28T23:00:00+0000").build()
        http_mocker.get(
            request,
            get_stream_response(_STREAM_NAME)
            .with_record(get_stream_record(_STREAM_NAME, "id", _CURSOR_FIELD).with_id(101).with_cursor("2024-02-02T00:00:00+00:00"))
            .build(),
        )
        output = read_incremental(self._config.with_lookback_window_days(3), _STREAM_NAME, state)
        assert [record.record.data["id"] for record in output.records] == [101]
        assert get_cursor_value_from_state_message(output, _CURSOR_FIELD) == "2024-02-02T00:00:00+0000"
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_state_message_produced_while_read_and_state_match_latest_record(self, http_mocker: HttpMocker) -> None:
        min_cursor_value = "2024-01-01T00:00:00+00:00"
        max_cursor_value = "2024-02-01T00:00:00+00:00"

        http_mocker.get(
            self.stream_request().with_limit(250).with_updated_at_min(START_DATE).build(),
            get_stream_response(_STREAM_NAME)
            .with_record(get_stream_record(_STREAM_NAME, "id", _CURSOR_FIELD).with_cursor(min_cursor_value))
            .with_record(get_stream_record(_STREAM_NAME, "id", _CURSOR_FIELD).with_cursor(max_cursor_value))
            .build(),
        )

        output = read_incremental(self._config, _STREAM_NAME)
        test_cursor_value = get_cursor_value_from_state_message(output, _CURSOR_FIELD)
        assert test_cursor_value == "2024-02-01T00:00:00+0000"

    @HttpMocker()
    def test_given_multiple_pages_when_read_then_return_records_with_state(self, http_mocker: HttpMocker) -> None:
        min_cursor_value = "2024-01-01T00:00:00+00:00"
        max_cursor_value = "2024-02-01T00:00:00+00:00"
        http_mocker.get(
            self.stream_request().with_limit(250).with_next_page_token(NEXT_PAGE_TOKEN).build(),
            get_stream_response(_STREAM_NAME).with_record(get_stream_record(_STREAM_NAME, "id", _CURSOR_FIELD)).build(),
        )
        http_mocker.get(
            self.stream_request().with_limit(250).with_updated_at_min(START_DATE).build(),
            get_stream_response(_STREAM_NAME)
            .with_pagination()
            .with_record(get_stream_record(_STREAM_NAME, "id", _CURSOR_FIELD).with_cursor(min_cursor_value))
            .with_record(get_stream_record(_STREAM_NAME, "id", _CURSOR_FIELD).with_cursor(max_cursor_value))
            .build(),
        )

        output = read_incremental(self._config, _STREAM_NAME)
        assert len(output.records) == 3
