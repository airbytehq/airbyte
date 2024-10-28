# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any
from unittest import TestCase

import pytest
import requests
import requests_mock
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http.error_handlers import ResponseAction
from requests.exceptions import ChunkedEncodingError
from source_salesforce.rate_limiting import BulkNotSupportedException, SalesforceErrorHandler

_ANY = "any"
_ANY_BASE_URL = "https://any-base-url.com"
_SF_API_VERSION = "v57.0"


class SalesforceErrorHandlerTest(TestCase):
    def setUp(self) -> None:
        self._error_handler = SalesforceErrorHandler()

    def test_given_invalid_entity_with_bulk_not_supported_message_on_job_creation_when_interpret_response_then_raise_bulk_not_supported(self) -> None:
        response = self._create_response("POST", self._url_for_job_creation(), 400, [{"errorCode": "INVALIDENTITY", "message": "X is not supported by the Bulk API"}])
        with pytest.raises(BulkNotSupportedException):
            self._error_handler.interpret_response(response)

    def test_given_compound_data_error_on_job_creation_when_interpret_response_then_raise_bulk_not_supported(self) -> None:
        response = self._create_response("POST", self._url_for_job_creation(), 400, [{"errorCode": _ANY, "message": "Selecting compound data not supported in Bulk Query"}])
        with pytest.raises(BulkNotSupportedException):
            self._error_handler.interpret_response(response)

    def test_given_request_limit_exceeded_on_job_creation_when_interpret_response_then_raise_bulk_not_supported(self) -> None:
        response = self._create_response("POST", self._url_for_job_creation(), 400, [{"errorCode": "REQUEST_LIMIT_EXCEEDED", "message": "Selecting compound data not supported in Bulk Query"}])
        with pytest.raises(BulkNotSupportedException):
            self._error_handler.interpret_response(response)

    def test_given_limit_exceeded_on_job_creation_when_interpret_response_then_raise_bulk_not_supported(self) -> None:
        response = self._create_response("POST", self._url_for_job_creation(), 400, [{"errorCode": "LIMIT_EXCEEDED", "message": _ANY}])
        with pytest.raises(BulkNotSupportedException):
            self._error_handler.interpret_response(response)

    def test_given_query_not_supported_on_job_creation_when_interpret_response_then_raise_bulk_not_supported(self) -> None:
        response = self._create_response("POST", self._url_for_job_creation(), 400, [{"errorCode": "API_ERROR", "message": "API does not support query"}])
        with pytest.raises(BulkNotSupportedException):
            self._error_handler.interpret_response(response)

    def test_given_txn_security_metering_error_when_interpret_response_then_raise_config_error(self) -> None:
        response = self._create_response("GET", self._url_for_job_creation() + "/job_id", 400, [{"errorCode": "TXN_SECURITY_METERING_ERROR", "message": "We can't complete the action because enabled transaction security policies took too long to complete."}])

        error_resolution = self._error_handler.interpret_response(response)

        assert error_resolution.response_action == ResponseAction.FAIL
        assert error_resolution.failure_type == FailureType.config_error

    def test_given_chunked_encoding_error_when_interpret_response_then_retry(self) -> None:
        error_resolution = self._error_handler.interpret_response(ChunkedEncodingError())
        assert error_resolution.response_action == ResponseAction.RETRY

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
        return f"{_ANY_BASE_URL}/services/data/{_SF_API_VERSION}/jobs/query"
