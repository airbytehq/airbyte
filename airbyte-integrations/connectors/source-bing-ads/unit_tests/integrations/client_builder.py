# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict

from airbyte_cdk.test.mock_http import HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


def response_with_status(resource: str, status_code: int) -> HttpResponse:
    return HttpResponse(json.dumps(find_template(resource, __file__)), status_code)


def build_request(config: Dict[str, Any]) -> HttpRequest:
    body = (
        f"client_id={config['client_id']}"
        f"&client_secret={config['client_secret']}"
        "&grant_type=refresh_token"
        f"&refresh_token={config['refresh_token']}"
        "&environment=production&scope=https%3A%2F%2Fads.microsoft.com%2Fmsads.manage+offline_access&oauth_scope=msads.manage"
        f"&tenant={config['tenant_id']}"
    )

    return HttpRequest(
        url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
        query_params={},
        body=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )


def build_request_2(config: Dict[str, Any]) -> HttpRequest:
    """
    This function is used to build a request for refreshing the OAuth token.
    We should just have temporarily having a second request builder as we are maintaining the client
    one and the declarative requester one. Once the client one is removed, the extra function can be removed as well.
    And probably the integration test will yell by then.
    The diff between the two is the order of the query parameters in the body.
    """
    body = (
        "grant_type=refresh_token"
        f"&client_id={config['client_id']}"
        f"&client_secret={config['client_secret']}"
        f"&refresh_token={config['refresh_token']}"
        "&environment=production"
        "&oauth_scope=msads.manage"
        "&scope=https%3A%2F%2Fads.microsoft.com%2Fmsads.manage+offline_access"
        f"&tenant={config['tenant_id']}"
    )

    return HttpRequest(
        url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
        query_params={},
        body=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
