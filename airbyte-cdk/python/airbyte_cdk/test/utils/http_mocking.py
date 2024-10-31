# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import re
from typing import Any, Mapping

from requests_mock import Mocker


def register_mock_responses(mocker: Mocker, http_calls: list[Mapping[str, Mapping[str, Any]]]) -> None:
    """Register a list of HTTP request-response pairs."""
    for call in http_calls:
        request, response = call["request"], call["response"]
        matcher = re.compile(request["url"]) if request["is_regex"] else request["url"]
        mocker.register_uri(request["method"], matcher, **response)
