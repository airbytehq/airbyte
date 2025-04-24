# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase
from unittest.mock import Mock

import pytest
from requests import HTTPError, Response
from source_salesforce.availability_strategy import SalesforceAvailabilityStrategy

from airbyte_cdk.sources.streams import Stream


_NO_SOURCE = None


class SalesforceAvailabilityStrategyTest(TestCase):
    def setUp(self) -> None:
        self._stream = Mock(spec=Stream)
        self._logger = Mock()
        self._error = HTTPError(response=Mock(spec=Response))

    def test_given_status_code_is_not_forbidden_or_bad_request_when_handle_http_error_then_raise_error(self) -> None:
        availability_strategy = SalesforceAvailabilityStrategy()
        self._error.response.status_code = 401

        with pytest.raises(HTTPError):
            availability_strategy.handle_http_error(self._stream, self._logger, _NO_SOURCE, self._error)

    def test_given_status_code_is_forbidden_when_handle_http_error_then_is_not_available_with_reason(self) -> None:
        availability_strategy = SalesforceAvailabilityStrategy()
        self._error.response.status_code = 403
        self._error.response.json.return_value = [{}]

        is_available, reason = availability_strategy.handle_http_error(self._stream, self._logger, _NO_SOURCE, self._error)

        assert not is_available
        assert reason

    def test_given_status_code_is_bad_request_when_handle_http_error_then_is_not_available_with_reason(self) -> None:
        availability_strategy = SalesforceAvailabilityStrategy()
        self._error.response.status_code = 400
        self._error.response.json.return_value = [{}]

        is_available, reason = availability_strategy.handle_http_error(self._stream, self._logger, _NO_SOURCE, self._error)

        assert not is_available
        assert reason

    def test_given_rate_limited_when_handle_http_error_then_is_available(self) -> None:
        availability_strategy = SalesforceAvailabilityStrategy()
        self._error.response.status_code = 400
        self._error.response.json.return_value = [{"errorCode": "REQUEST_LIMIT_EXCEEDED"}]

        is_available, reason = availability_strategy.handle_http_error(self._stream, self._logger, _NO_SOURCE, self._error)

        assert is_available
        assert reason is None
