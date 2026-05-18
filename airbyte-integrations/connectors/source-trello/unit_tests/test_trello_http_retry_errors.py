# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from unittest.mock import MagicMock, patch

import pytest

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http import HttpClient
from airbyte_cdk.sources.streams.http.error_handlers import ErrorResolution, HttpStatusErrorHandler, ResponseAction
from airbyte_cdk.sources.streams.http.exceptions import UserDefinedBackoffException
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


class TrelloConstantBackoffStrategy:
    @staticmethod
    def backoff_time(response_or_exception, attempt_count):
        return 0.1


def test_trello_http_500_retry_exhaustion_preserves_transient_error_message(requests_mock):
    error_message = "Internal server error."
    http_client = HttpClient(
        name="actions",
        logger=MagicMock(spec=logging.Logger),
        error_handler=HttpStatusErrorHandler(
            logger=MagicMock(),
            error_mapping={
                500: ErrorResolution(ResponseAction.RETRY, FailureType.transient_error, error_message),
            },
            max_retries=1,
        ),
        backoff_strategy=TrelloConstantBackoffStrategy(),
    )

    requests_mock.get(
        "https://api.trello.com/1/boards/board_id/actions",
        [
            {"status_code": 500, "text": error_message, "headers": {}},
            {"status_code": 500, "text": error_message, "headers": {}},
        ],
    )

    with patch("airbyte_cdk.sources.streams.http.rate_limiting.time.sleep"):
        with pytest.raises(AirbyteTracedException) as exc_info:
            http_client.send_request(
                http_method="get",
                url="https://api.trello.com/1/boards/board_id/actions",
                request_kwargs={},
            )

    traced_exception = exc_info.value
    assert traced_exception.failure_type == FailureType.transient_error
    assert traced_exception.message == (
        "Exhausted available request attempts. Please see logs for more details. Exception: Internal server error."
    )
    assert traced_exception.internal_message == ("Exhausted available request attempts. Exception: Internal server error.")
    assert isinstance(traced_exception._exception, UserDefinedBackoffException)
    assert traced_exception._exception.response.status_code == 500
