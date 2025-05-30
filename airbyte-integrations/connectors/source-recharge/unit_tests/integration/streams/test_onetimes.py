#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from unittest import TestCase

import freezegun
from airbyte_cdk.test.mock_http import HttpMocker

from ..config import NOW, START_DATE
from ..response_builder import NEXT_PAGE_TOKEN, get_stream_record, get_stream_response
from ..utils import StreamTestCase, config, get_cursor_value_from_state_message, read_full_refresh, read_incremental

_STREAM_NAME = "onetimes"
_CURSOR_FIELD = "updated_at"


@freezegun.freeze_time(NOW.isoformat())
class TestFullRefresh(StreamTestCase):
    _STREAM_NAME = "onetimes"

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
    _STREAM_NAME = "onetimes"

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
        assert test_cursor_value == max_cursor_value

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
