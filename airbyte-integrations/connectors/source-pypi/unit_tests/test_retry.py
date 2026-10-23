from unittest.mock import Mock

import requests

from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution, ResponseAction


def test_retry_uses_backoff(monkeypatch):
    handler = DefaultErrorHandler(parameters={}, config={})
    monkeypatch.setattr(
        handler,
        "interpret_response",
        lambda response: ErrorResolution(response_action=ResponseAction.RETRY),
    )
    backoff = Mock(return_value=2)
    monkeypatch.setattr(handler, "backoff_time", backoff)
    response = requests.Response()

    assert handler.interpret_response(response).response_action is ResponseAction.RETRY
    handler.backoff_time(response, attempt_count=1)
    backoff.assert_called_once_with(response, attempt_count=1)
