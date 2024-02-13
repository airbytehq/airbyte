from typing import Dict, Any

from airbyte_cdk.test.mock_http import HttpRequest
import json

from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


def response_with_status(resource: str, status_code: int) -> HttpResponse:
    return HttpResponse(json.dumps(find_template(resource, __file__)), status_code)


def build_request(config: Dict[str, Any]):
    # "client_id=test-client-id&client_secret=test-client-secret&grant_type=refresh_token&refresh_token=test-refresh-token&environment=
    # production&scope=https%3A%2F%2Fads.microsoft.com%2Fmsads.manage+offline_access&oauth_scope=msads.manage&tenant=common",

    body = f"client_id={config['client_id']}"
    body += f"&client_secret={config['client_secret']}"
    body += "&grant_type=refresh_token"
    body += f"&refresh_token={config['refresh_token']}"
    body += "&environment=production&scope=https%3A%2F%2Fads.microsoft.com%2Fmsads.manage+offline_access&oauth_scope=msads.manage"
    body += f"&tenant={config['tenant_id']}"

    return HttpRequest(
        url=f"https://login.microsoftonline.com/common/oauth2/v2.0/token",
        query_params={},
        body=body,
        headers={'User-Agent': 'python-requests/2.31.0', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*',
                 'Connection': 'keep-alive', 'Content-Length': '245', 'Content-Type': 'application/x-www-form-urlencoded'},
    )
