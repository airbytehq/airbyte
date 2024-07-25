import json
from http import HTTPStatus
from typing import Union, Mapping, Any, List, Optional
from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


def build_response(
        body: Union[Mapping[str, Any], List[Mapping[str, Any]]],
        status_code: HTTPStatus,
        headers: Optional[Mapping[str, str]] = None,
) -> HttpResponse:
    headers = headers or {}
    return HttpResponse(body=json.dumps(body), status_code=status_code.value, headers=headers)


def get_customers_response(path: str, status_code: int) -> HttpResponse:
    with open(path) as f:
        response = f.read()
    return HttpResponse(response, status_code)
