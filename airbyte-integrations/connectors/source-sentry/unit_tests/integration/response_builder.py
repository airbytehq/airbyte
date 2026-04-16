# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


def create_response(resource_name: str, status_code: int = 200, has_next: bool = False, cursor: str = "next") -> HttpResponse:
    """
    Create HTTP response using template from resource/http/response/<resource_name>.json

    Args:
        resource_name: Name of the JSON file (without .json extension)
        status_code: HTTP status code
        has_next: Whether there's a next page (for pagination)
        cursor: Cursor value for pagination
    """
    body = json.dumps(find_template(resource_name, __file__))

    headers = {}
    if has_next:
        headers["link"] = f'<https://sentry.io/api/0/.../?cursor={cursor}>; rel="next"; results="true"; cursor="{cursor}"'
    else:
        headers["link"] = f'<https://sentry.io/api/0/.../?cursor={cursor}>; rel="next"; results="false"; cursor="{cursor}"'

    # Add rate limit headers
    headers["X-Sentry-Rate-Limit-Limit"] = "50"
    headers["X-Sentry-Rate-Limit-Remaining"] = "45"
    headers["X-Sentry-Rate-Limit-Reset"] = "1732512000"

    return HttpResponse(body, status_code, headers)


def error_response(status_code: int) -> HttpResponse:
    """Create error response (401, 429, etc.)"""
    body = json.dumps(find_template(str(status_code), __file__))

    headers = {}
    if status_code == 429:
        headers["Retry-After"] = "60"

    return HttpResponse(body, status_code, headers)
