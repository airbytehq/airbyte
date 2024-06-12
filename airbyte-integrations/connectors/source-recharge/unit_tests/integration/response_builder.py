#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import json
from http import HTTPStatus
from typing import Any, List, Mapping, Optional, Union

from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponseBuilder,
    RecordBuilder,
    create_record_builder,
    create_response_builder,
    find_template,
)

from .pagination import NEXT_PAGE_TOKEN, RechargePaginationStrategy
from .request_builder import get_stream_request


def build_response(
    body: Union[Mapping[str, Any], List[Mapping[str, Any]]],
    status_code: HTTPStatus,
    headers: Optional[Mapping[str, str]] = None,
) -> HttpResponse:
    headers = headers or {}
    return HttpResponse(
        body=json.dumps(body),
        status_code=status_code.value,
        headers=headers,
    )


def get_stream_response(stream_name: str) -> HttpResponseBuilder:
    return create_response_builder(
        response_template=find_template(stream_name, __file__),
        records_path=FieldPath(stream_name),
        pagination_strategy=RechargePaginationStrategy(
            request=get_stream_request(stream_name).build(),
            next_page_token=NEXT_PAGE_TOKEN,
        ),
    )


def get_stream_record(
    stream_name: str,
    record_id_path: str,
    cursor_field: Optional[str] = None,
) -> RecordBuilder:
    return create_record_builder(
        response_template=find_template(stream_name, __file__),
        records_path=FieldPath(stream_name),
        record_id_path=FieldPath(record_id_path),
        record_cursor_path=FieldPath(cursor_field) if cursor_field else None,
    )
