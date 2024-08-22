#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import json
from http import HTTPStatus
from typing import Any, List, Mapping, Optional, Union

from airbyte_cdk.test.mock_http import HttpResponse

from .config import BUSINESS_ACCOUNT_ID, PAGE_ID


def build_response(
    body: Union[Mapping[str, Any], List[Mapping[str, Any]]],
    status_code: HTTPStatus,
    headers: Optional[Mapping[str, str]] = None,
) -> HttpResponse:
    headers = headers or {}
    return HttpResponse(body=json.dumps(body), status_code=status_code.value, headers=headers)


def get_account_response() -> HttpResponse:
    response = {
            "data": [
                {
                    "id": PAGE_ID,
                    "name": "AccountName",
                    "instagram_business_account": {
                        "id": BUSINESS_ACCOUNT_ID
                    }
                }
            ],
            "paging": {
                "cursors": {
                    "before": "before_token",
                    "after": "after_token"
                }
            }
        }
    return build_response(body=response, status_code=HTTPStatus.OK)
