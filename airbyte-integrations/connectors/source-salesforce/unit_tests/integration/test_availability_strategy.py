# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase
from unittest.mock import Mock

import pytest
from requests import exceptions
from source_salesforce.availability_strategy import SalesforceAvailabilityStrategy

from integration.utils import create_base_url


_INSTANCE_URL = "https://instance.salesforce.com"
_STREAM_NAME = "StreamName"

_BASE_URL = create_base_url(_INSTANCE_URL)


class AvailabilityStrategyTest(TestCase):
    def setUp(self) -> None:
        self._strategy = SalesforceAvailabilityStrategy()

    def test_handle_http_error_with_json_decode_error_then_raise_exception(self) -> None:
        mock_response = Mock()
        mock_response.json.side_effect = exceptions.JSONDecodeError("Expecting value", "<html>Error</html>", 0)
        http_error = exceptions.HTTPError(response=mock_response)
        http_error.response.status_code = 403

        with pytest.raises(exceptions.HTTPError) as exception:
            self._strategy.handle_http_error(Mock(), Mock(), Mock(), http_error)

        assert type(exception.value.__cause__) == exceptions.JSONDecodeError
        assert type(exception.value) == exceptions.HTTPError
        assert exception.value == http_error

    def test_handle_http_error_with_forbidden_and_request_limit_exceeded_error_code_then_return_tuple(self) -> None:
        mock_response = Mock()
        mock_response.json.return_value = [{"errorCode": "REQUEST_LIMIT_EXCEEDED"}]
        http_error = exceptions.HTTPError(response=mock_response)
        http_error.response.status_code = 403

        stream = Mock()
        stream.name = _STREAM_NAME

        output = self._strategy.handle_http_error(stream, Mock(), Mock(), http_error)

        assert output == (True, None)

    def test_handle_http_error_with_bad_request_and_request_limit_exceeded_error_code_then_return_tuple(self) -> None:
        mock_response = Mock()
        mock_response.json.return_value = [{"errorCode": "REQUEST_LIMIT_EXCEEDED"}]
        http_error = exceptions.HTTPError(response=mock_response)
        http_error.response.status_code = 400

        stream = Mock()
        stream.name = _STREAM_NAME

        output = self._strategy.handle_http_error(stream, Mock(), Mock(), http_error)

        assert output == (True, None)

    def test_handle_http_error_with_other_error_code_then_return_tuple(self) -> None:
        mock_response = Mock()
        mock_response.json.return_value = [{"errorCode": "OTHER_ERROR_CODE", "message": "OTHER_ERROR_MESSAGE"}]
        http_error = exceptions.HTTPError(response=mock_response)
        http_error.response.status_code = 403

        stream = Mock()
        stream.name = _STREAM_NAME

        output = self._strategy.handle_http_error(stream, Mock(), Mock(), http_error)

        assert output == (False, f"Cannot receive data for stream '{_STREAM_NAME}', error message: 'OTHER_ERROR_MESSAGE'")

    def test_handle_http_error_with_server_error_code_then_raise_exception(self) -> None:
        mock_response = Mock()
        http_error = exceptions.HTTPError(response=mock_response)
        http_error.response.status_code = 500

        with pytest.raises(exceptions.HTTPError) as exception:
            self._strategy.handle_http_error(Mock(), Mock(), Mock(), http_error)

        assert type(exception.value) == exceptions.HTTPError
        assert exception.value == http_error
