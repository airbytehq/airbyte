# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest.mock import PropertyMock, patch

import pytest
import requests
from components import BingAdsDownloadErrorHandler

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


@pytest.mark.parametrize("status_code", [200, 204])
def test_success_does_not_read_body(status_code):
    response = requests.Response()
    response.status_code = status_code
    handler = BingAdsDownloadErrorHandler(config={}, parameters={})
    with patch.object(requests.Response, "content", new_callable=PropertyMock, side_effect=AssertionError("Body consumed")):
        resolution = handler.interpret_response(response)
    assert resolution.response_action == ResponseAction.SUCCESS


@pytest.mark.parametrize("body", [b"", b"<Error><Code>AuthorizationPermissionMismatch</Code></Error>"])
def test_other_forbidden_responses_keep_default_handling(body):
    response = requests.Response()
    response.status_code = 403
    response._content = body
    handler = BingAdsDownloadErrorHandler(config={}, parameters={})
    resolution = handler.interpret_response(response)
    assert resolution.response_action == ResponseAction.FAIL
    assert resolution.failure_type == FailureType.config_error
