#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from typing import Optional, Union

import requests
from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.utils.airbyte_secrets_utils import filter_secrets


def format_http_json(response: requests.Response, logger: str):
    request = response.request
    log_message = {
        "http": {
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
            "logger": logger,
            "level": "debug",
        },
        "url": {"full": request.url},
    }
    return filter_secrets(json.dumps(log_message))


def create_airbyte_log_message(response: requests.Response, logger: str):
    return AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=Level.DEBUG, message=format_http_json(response, logger)))


def create_new_log_with_updated_logger(log: str, logger: str) -> str:
    """
    Only supports HTTP logs. If log is not HTTP, will raise ValueError
    """
    try:
        log_as_json = json.loads(log)
        if "http" not in log_as_json:
            raise ValueError(f"Log is not HTTP")
        log_as_json["log"]["logger"] = logger
        return json.dumps(log_as_json)
    except json.JSONDecodeError:
        return False


def _normalize_body_string(body_str: Optional[Union[str, bytes]]) -> Optional[str]:
    return body_str.decode() if isinstance(body_str, (bytes, bytearray)) else body_str
