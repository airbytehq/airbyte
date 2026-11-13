# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


DEPRECATED_TOKEN_MESSAGE = (
    "OneSignal rejected the User Auth Key because it uses a deprecated v1 format. "
    "Generate an Organization API key in OneSignal and enter it in the User Auth Key field."
)
CONFIG = {"user_auth_key": "test-user-key", "start_date": "2024-01-01T00:00:00Z", "applications": [], "outcome_names": ""}


class TestAppsErrorHandling(TestCase):
    @HttpMocker()
    def test_deprecated_token_is_config_error_without_retry(self, http_mocker: HttpMocker) -> None:
        request = HttpRequest(url="https://onesignal.com/api/v1/apps", headers={"Authorization": "Basic test-user-key"})
        http_mocker.get(
            request,
            HttpResponse(
                body=json.dumps(
                    {"errors": ["Request is malformed: Auth token is a deprecated v1 user token format. Please migrate to v2 org tokens."]}
                ),
                status_code=400,
            ),
        )

        output = read(
            get_source(CONFIG),
            config=CONFIG,
            catalog=CatalogBuilder().with_stream("apps", SyncMode.full_refresh).build(),
            expecting_exception=True,
        )

        assert not output.records
        assert output.errors
        assert all(error.trace.error.failure_type == FailureType.config_error for error in output.errors)
        assert any(error.trace.error.message == DEPRECATED_TOKEN_MESSAGE for error in output.errors)
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_unrelated_bad_request_preserves_generic_error(self, http_mocker: HttpMocker) -> None:
        request = HttpRequest(url="https://onesignal.com/api/v1/apps")
        http_mocker.get(request, HttpResponse(body=json.dumps({"errors": ["Unrelated malformed request"]}), status_code=400))

        output = read(
            get_source(CONFIG),
            config=CONFIG,
            catalog=CatalogBuilder().with_stream("apps", SyncMode.full_refresh).build(),
            expecting_exception=True,
        )

        assert not output.records
        assert output.errors
        stream_errors = [error.trace.error for error in output.errors if error.trace.error.stream_descriptor]
        assert len(stream_errors) == 1
        assert stream_errors[0].failure_type == FailureType.system_error
        assert any(
            error.trace.error.failure_type == FailureType.system_error
            and error.trace.error.message == "HTTP Status Code: 400. Error: Bad request. Please check your request parameters."
            for error in output.errors
        )
        assert all(DEPRECATED_TOKEN_MESSAGE not in error.trace.error.message for error in output.errors)
        http_mocker.assert_number_of_calls(request, 1)
