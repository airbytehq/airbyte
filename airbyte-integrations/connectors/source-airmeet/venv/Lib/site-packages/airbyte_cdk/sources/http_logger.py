#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Optional, Union

import requests

from airbyte_cdk.sources.message import LogMessage


def format_http_message(
    response: requests.Response,
    title: str,
    description: str,
    stream_name: Optional[str],
    is_auxiliary: bool | None = None,
    type: Optional[str] = None,
) -> LogMessage:
    request_type: str = type if type else "HTTP"
    request = response.request
    log_message = {
        "http": {
            "title": title,
            "type": request_type,
            "description": description,
            "request": {
                "method": request.method,
                "body": {
                    "content": _normalize_body_string(request.body),
                },
                "headers": dict(request.headers),
            },
            "response": {
                "body": {
                    "content": response.text,
                },
                "headers": dict(response.headers),
                "status_code": response.status_code,
            },
        },
        "log": {
            "level": "debug",
        },
        "url": {"full": request.url},
    }
    if is_auxiliary is not None:
        log_message["http"]["is_auxiliary"] = is_auxiliary  # type: ignore [index]
    if stream_name:
        log_message["airbyte_cdk"] = {"stream": {"name": stream_name}}
    return log_message  # type: ignore[return-value]  # got "dict[str, object]", expected "dict[str, JsonType]"


def _normalize_body_string(body_str: Optional[Union[str, bytes]]) -> Optional[str]:
    return body_str.decode() if isinstance(body_str, (bytes, bytearray)) else body_str
