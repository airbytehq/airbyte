#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


from http import HTTPStatus
from unittest import TestCase

import freezegun
from requests import Response

from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_protocol.models import FailureType

from ..config import NOW
from ..response_builder import NEXT_PAGE_TOKEN, get_stream_record, get_stream_response
from ..utils import StreamTestCase, read_full_refresh, source


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

    def test_given_gateway_timeout_when_interpret_response_then_error_has_stream_context(self) -> None:
        payment_methods_stream = next(stream for stream in source().streams(self._config.build()) if stream.name == _STREAM_NAME)
        response = Response()
        response.status_code = HTTPStatus.GATEWAY_TIMEOUT.value

        error_resolution = payment_methods_stream.retriever.requester.error_handler.interpret_response(response)

        assert error_resolution.response_action == ResponseAction.RETRY
        assert error_resolution.failure_type == FailureType.transient_error
        assert error_resolution.error_message == "Recharge API request timed out for stream payment_methods."
