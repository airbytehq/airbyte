#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


from unittest import TestCase

import freezegun

from airbyte_cdk.test.mock_http import HttpMocker

from ..config import NOW
from ..response_builder import NEXT_PAGE_TOKEN, get_stream_record, get_stream_response
from ..utils import StreamTestCase, read_full_refresh


_STREAM_NAME = "payment_methods"


@freezegun.freeze_time(NOW.isoformat())
class TestFullRefresh(StreamTestCase):
    _STREAM_NAME = _STREAM_NAME

    @HttpMocker()
    def test_given_one_page_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            self.stream_request().with_limit(250).build(),
            get_stream_response(_STREAM_NAME).with_record(get_stream_record(_STREAM_NAME, "id")).build(),
        )
        output = read_full_refresh(self._config, _STREAM_NAME)
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_multiple_pages_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            self.stream_request().with_limit(250).with_next_page_token(NEXT_PAGE_TOKEN).build(),
            get_stream_response(_STREAM_NAME).with_record(get_stream_record(_STREAM_NAME, "id")).build(),
        )
        http_mocker.get(
            self.stream_request().with_limit(250).build(),
            get_stream_response(_STREAM_NAME).with_pagination().with_record(get_stream_record(_STREAM_NAME, "id")).build(),
        )

        output = read_full_refresh(self._config, _STREAM_NAME)
        assert len(output.records) == 2
