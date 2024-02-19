#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import json
from http import HTTPStatus
from typing import Any, List, Mapping, Optional, Union

from airbyte_cdk.test.mock_http import HttpResponse

from .config import ACCOUNT_ID


def build_response(
    body: Union[Mapping[str, Any], List[Mapping[str, Any]]],
    status_code: HTTPStatus,
    headers: Optional[Mapping[str, str]] = None,
) -> HttpResponse:
    headers = headers or {}
    return HttpResponse(body=json.dumps(body), status_code=status_code.value, headers=headers)


def get_account_response(account_id: Optional[str] = ACCOUNT_ID) -> HttpResponse:
    response = {"account_id": account_id, "id": f"act_{account_id}"}
    return build_response(body=response, status_code=HTTPStatus.OK)


def error_reduce_amount_of_data_response() -> HttpResponse:
    response = {
        "error": {"code": 1, "message": "Please reduce the amount of data you're asking for, then retry your request"},
    }
    return build_response(body=response, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
