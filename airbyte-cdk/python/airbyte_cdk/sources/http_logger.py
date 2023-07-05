import json
import requests

from typing import Optional, Union

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level, SyncMode
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
            }
        },
        "log": {
            "logger": logger,
            "level": "debug",
        },
        "url": {
            "full": request.url
        }
    }
    return filter_secrets(json.dumps(log_message))


def create_airbyte_log_message(response: requests.Response, logger: str):
    return AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=Level.DEBUG, message=format_http_json(response, logger)))


def _normalize_body_string(body_str: Optional[Union[str, bytes]]) -> Optional[str]:
    return body_str.decode() if isinstance(body_str, (bytes, bytearray)) else body_str
