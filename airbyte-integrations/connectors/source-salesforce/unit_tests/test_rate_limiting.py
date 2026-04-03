# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest
import requests
import requests_mock
from requests.exceptions import ChunkedEncodingError
from source_salesforce.api import _TOKEN_REFRESH_INTERVAL_SECONDS, API_VERSION, SalesforceTokenProvider
from source_salesforce.rate_limiting import BulkNotSupportedException, SalesforceErrorHandler

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http.error_handlers import ResponseAction


_ANY = "any"
_ANY_BASE_URL = "https://any-base-url.com"


class SalesforceTokenProviderTest(TestCase):
    def setUp(self) -> None:
        self._sf_api = MagicMock()
        self._sf_api.access_token = "initial_token"
        self._token_provider = SalesforceTokenProvider(self._sf_api)

    def test_get_token_returns_token_without_login_when_within_refresh_interval(self) -> None:
        token = self._token_provider.get_token()

        assert token == "initial_token"
        self._sf_api.login.assert_not_called()

    def test_get_token_calls_login_when_interval_elapsed(self) -> None:
        self._sf_api.access_token = "refreshed_token"
        with patch("source_salesforce.api.time.monotonic", side_effect=[0.0, _TOKEN_REFRESH_INTERVAL_SECONDS + 1, 0.0]):
            provider = SalesforceTokenProvider(self._sf_api)
            token = provider.get_token()

        self._sf_api.login.assert_called_once()
        assert token == "refreshed_token"

    def test_get_token_returns_existing_token_when_login_fails(self) -> None:
        self._sf_api.login.side_effect = Exception("network error")
        self._sf_api.access_token = "stale_token"
        with patch("source_salesforce.api.time.monotonic", side_effect=[0.0, _TOKEN_REFRESH_INTERVAL_SECONDS + 1]):
            provider = SalesforceTokenProvider(self._sf_api)
            token = provider.get_token()

        self._sf_api.login.assert_called_once()
        assert token == "stale_token"

    def test_force_refresh_calls_login_immediately(self) -> None:
        self._token_provider.force_refresh()

        self._sf_api.login.assert_called_once()

    def test_force_refresh_does_not_raise_when_login_fails(self) -> None:
        self._sf_api.login.side_effect = Exception("network error")

        self._token_provider.force_refresh()  # should not raise

        self._sf_api.login.assert_called_once()


class SalesforceErrorHandlerTest(TestCase):
    def setUp(self) -> None:
        self._error_handler = SalesforceErrorHandler()

    def test_given_invalid_entity_with_bulk_not_supported_message_on_job_creation_when_interpret_response_then_raise_bulk_not_supported(
        self,
    ) -> None:
        response = self._create_response(
            "POST", self._url_for_job_creation(), 400, [{"errorCode": "INVALIDENTITY", "message": "X is not supported by the Bulk API"}]
        )
        with pytest.raises(BulkNotSupportedException):
            self._error_handler.interpret_response(response)

    def test_given_compound_data_error_on_job_creation_when_interpret_response_then_raise_bulk_not_supported(self) -> None:
        response = self._create_response(
            "POST",
            self._url_for_job_creation(),
            400,
            [{"errorCode": _ANY, "message": "Selecting compound data not supported in Bulk Query"}],
        )
        with pytest.raises(BulkNotSupportedException):
            self._error_handler.interpret_response(response)

    def test_given_request_limit_exceeded_on_job_creation_when_interpret_response_then_raise_bulk_not_supported(self) -> None:
        response = self._create_response(
            "POST",
            self._url_for_job_creation(),
            400,
            [{"errorCode": "REQUEST_LIMIT_EXCEEDED", "message": "Selecting compound data not supported in Bulk Query"}],
        )
        with pytest.raises(BulkNotSupportedException):
            self._error_handler.interpret_response(response)

    def test_given_limit_exceeded_on_job_creation_when_interpret_response_then_raise_bulk_not_supported(self) -> None:
        response = self._create_response("POST", self._url_for_job_creation(), 400, [{"errorCode": "LIMIT_EXCEEDED", "message": _ANY}])
        with pytest.raises(BulkNotSupportedException):
            self._error_handler.interpret_response(response)

    def test_given_query_not_supported_on_job_creation_when_interpret_response_then_raise_bulk_not_supported(self) -> None:
        response = self._create_response(
            "POST", self._url_for_job_creation(), 400, [{"errorCode": "API_ERROR", "message": "API does not support query"}]
        )
        with pytest.raises(BulkNotSupportedException):
            self._error_handler.interpret_response(response)

    def test_given_txn_security_metering_error_when_interpret_response_then_raise_config_error(self) -> None:
        response = self._create_response(
            "GET",
            self._url_for_job_creation() + "/job_id",
            400,
            [
                {
                    "errorCode": "TXN_SECURITY_METERING_ERROR",
                    "message": "We can't complete the action because enabled transaction security policies took too long to complete.",
                }
            ],
        )

        error_resolution = self._error_handler.interpret_response(response)

        assert error_resolution.response_action == ResponseAction.FAIL
        assert error_resolution.failure_type == FailureType.config_error

    def test_given_chunked_encoding_error_when_interpret_response_then_retry(self) -> None:
        error_resolution = self._error_handler.interpret_response(ChunkedEncodingError())
        assert error_resolution.response_action == ResponseAction.RETRY

    def test_given_401_invalid_session_id_with_token_provider_when_interpret_response_then_retry_and_refresh(self) -> None:
        token_provider = MagicMock()
        error_handler = SalesforceErrorHandler(token_provider=token_provider)
        response = self._create_response(
            "GET",
            f"{_ANY_BASE_URL}/services/data/{API_VERSION}/sobjects",
            401,
            [{"errorCode": "INVALID_SESSION_ID", "message": "Session expired or invalid"}],
        )

        error_resolution = error_handler.interpret_response(response)

        assert error_resolution.response_action == ResponseAction.RETRY
        assert error_resolution.failure_type == FailureType.transient_error
        token_provider.force_refresh.assert_called_once()

    def test_given_401_invalid_session_id_without_token_provider_when_interpret_response_then_retry_without_crash(self) -> None:
        error_handler = SalesforceErrorHandler(token_provider=None)
        response = self._create_response(
            "GET",
            f"{_ANY_BASE_URL}/services/data/{API_VERSION}/sobjects",
            401,
            [{"errorCode": "INVALID_SESSION_ID", "message": "Session expired or invalid"}],
        )

        error_resolution = error_handler.interpret_response(response)

        assert error_resolution.response_action == ResponseAction.RETRY
        assert error_resolution.failure_type == FailureType.transient_error

    def test_given_401_with_different_error_code_when_interpret_response_then_fall_through(self) -> None:
        response = self._create_response(
            "GET",
            f"{_ANY_BASE_URL}/services/data/{API_VERSION}/sobjects",
            401,
            [{"errorCode": "SOME_OTHER_ERROR", "message": "some message"}],
        )

        error_resolution = self._error_handler.interpret_response(response)

        # 401 is a 4xx that is NOT in _RETRYABLE_400_STATUS_CODES, so it should FAIL
        assert error_resolution.response_action == ResponseAction.FAIL

    def _create_response(self, http_method: str, url: str, status_code: int, json: Any) -> requests.Response:
        with requests_mock.Mocker() as mocker:
            mocker.register_uri(
                http_method,
                url,
                status_code=status_code,
                json=json,
            )
            return requests.request(http_method, url)

    def _url_for_job_creation(self) -> str:
        return f"{_ANY_BASE_URL}/services/data/{API_VERSION}/jobs/query"
