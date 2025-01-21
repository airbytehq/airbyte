# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase

import requests
import requests_mock
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction, create_fallback_error_resolution
from airbyte_cdk.utils.airbyte_secrets_utils import update_secrets

_A_SECRET = "a-secret"
_A_URL = "https://a-url.com"


class DefaultErrorResolutionTest(TestCase):
    def setUp(self) -> None:
        update_secrets([_A_SECRET])

    def tearDown(self) -> None:
        # to avoid other tests being impacted by added secrets
        update_secrets([])

    def test_given_none_when_create_fallback_error_resolution_then_return_error_resolution(self) -> None:
        error_resolution = create_fallback_error_resolution(None)

        assert error_resolution.failure_type == FailureType.system_error
        assert error_resolution.response_action == ResponseAction.RETRY
        assert (
            error_resolution.error_message
            == "Error handler did not receive a valid response or exception. This is unexpected please contact Airbyte Support"
        )

    def test_given_exception_when_create_fallback_error_resolution_then_return_error_resolution(self) -> None:
        exception = ValueError("This is an exception")

        error_resolution = create_fallback_error_resolution(exception)

        assert error_resolution.failure_type == FailureType.system_error
        assert error_resolution.response_action == ResponseAction.RETRY
        assert error_resolution.error_message
        assert "ValueError" in error_resolution.error_message
        assert str(exception) in error_resolution.error_message

    def test_given_response_can_raise_for_status_when_create_fallback_error_resolution_then_error_resolution(self) -> None:
        response = self._create_response(512)

        error_resolution = create_fallback_error_resolution(response)

        assert error_resolution.failure_type == FailureType.system_error
        assert error_resolution.response_action == ResponseAction.RETRY
        assert error_resolution.error_message and "512 Server Error: None for url: https://a-url.com/" in error_resolution.error_message

    def test_given_response_is_ok_when_create_fallback_error_resolution_then_error_resolution(self) -> None:
        response = self._create_response(205)

        error_resolution = create_fallback_error_resolution(response)

        assert error_resolution.failure_type == FailureType.system_error
        assert error_resolution.response_action == ResponseAction.RETRY
        assert error_resolution.error_message and str(response.status_code) in error_resolution.error_message

    def _create_response(self, status_code: int) -> requests.Response:
        with requests_mock.Mocker() as http_mocker:
            http_mocker.get(_A_URL, status_code=status_code)
            return requests.get(_A_URL)
