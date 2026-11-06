#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import re
import uuid
from enum import Enum
from typing import Any, List, Mapping, MutableMapping, Optional

import requests

from airbyte_cdk.sources.streams.http.requests_native_auth.oauth import Oauth2Authenticator


logger = logging.getLogger("airbyte")


class MicrosoftOauth2Authenticator(Oauth2Authenticator):
    def build_refresh_request_body(self) -> Mapping[str, Any]:
        """
        Returns the request body to set on the refresh request
        """
        payload: MutableMapping[str, Any] = {
            "grant_type": "client_credentials",
            "client_id": self.get_client_id(),
            "client_secret": self.get_client_secret(),
            "scope": self.get_scopes(),
        }

        return payload


class AirbyteType(Enum):
    String = {"type": ["null", "string"]}
    Boolean = {"type": ["null", "boolean"]}
    Timestamp = {"type": ["null", "string"], "format": "date-time", "airbyte_type": "timestamp_with_timezone"}
    Date = {"type": ["null", "string"], "format": "date"}
    Integer = {"type": ["null", "integer"]}
    Number = {"type": ["null", "number"]}


class DataverseType(Enum):
    String = AirbyteType.String
    Uniqueidentifier = AirbyteType.String
    DateTime = AirbyteType.Timestamp
    Integer = AirbyteType.Integer
    BigInt = AirbyteType.Integer
    Money = AirbyteType.Number
    Boolean = AirbyteType.Boolean
    Double = AirbyteType.Number
    Decimal = AirbyteType.Number
    Status = AirbyteType.Integer
    State = AirbyteType.Integer
    Picklist = AirbyteType.Integer
    Lookup = AirbyteType.String
    Virtual = None


def get_auth(config: Mapping[str, Any]) -> MicrosoftOauth2Authenticator:
    return MicrosoftOauth2Authenticator(
        token_refresh_endpoint=f'https://login.microsoftonline.com/{config["tenant_id"]}/oauth2/v2.0/token',
        client_id=config["client_id"],
        client_secret=config["client_secret_value"],
        scopes=[f'{config["url"]}/.default'],
        refresh_token="",
    )


def do_request(config: Mapping[str, Any], path: str):
    auth = get_auth(config)
    headers = auth.get_auth_header()
    # Call a protected API with the access token.
    return requests.get(
        config["url"] + "/api/data/v9.2/" + path,
        headers=headers,
    )


def convert_dataverse_type(dataverse_type: str, datetime_behavior: Optional[str] = None) -> Optional[dict]:
    if dataverse_type == "DateTime" and datetime_behavior == "DateOnly":
        return AirbyteType.Date.value

    if dataverse_type in DataverseType.__members__:
        enum_type = DataverseType[dataverse_type]
        if enum_type:
            return enum_type.value if enum_type.value is None else enum_type.value.value

    return AirbyteType.String.value


BATCH_SIZE = 1000


def get_all_datetime_behaviors(config: Mapping[str, Any], entity_names: List[str]) -> Mapping[str, Mapping[str, str]]:
    """Query DateTimeBehavior for multiple entities using OData $batch requests.

    Returns a mapping of entity_name -> {attribute_logical_name -> behavior_value}.
    Requests are grouped into batches of up to 1000 per the Dataverse $batch limit.
    """
    if not entity_names:
        return {}

    all_behaviors: dict[str, Mapping[str, str]] = {}
    for i in range(0, len(entity_names), BATCH_SIZE):
        batch = entity_names[i : i + BATCH_SIZE]
        batch_result = _execute_batch_datetime_request(config, batch)
        all_behaviors.update(batch_result)
    return all_behaviors


def _execute_batch_datetime_request(config: Mapping[str, Any], entity_names: List[str]) -> Mapping[str, Mapping[str, str]]:
    """Execute a single $batch POST for DateTimeBehavior metadata."""
    auth = get_auth(config)
    headers = auth.get_auth_header()

    batch_id = str(uuid.uuid4())
    boundary = f"batch_{batch_id}"
    headers["Content-Type"] = f'multipart/mixed; boundary="{boundary}"'

    parts: list[str] = []
    for entity_name in entity_names:
        path = (
            f"EntityDefinitions(LogicalName='{entity_name}')"
            f"/Attributes/Microsoft.Dynamics.CRM.DateTimeAttributeMetadata"
            f"?$select=LogicalName,DateTimeBehavior"
        )
        parts.append(
            f"--{boundary}\r\n"
            f"Content-Type: application/http\r\n"
            f"Content-Transfer-Encoding: binary\r\n"
            f"\r\n"
            f"GET /api/data/v9.2/{path} HTTP/1.1\r\n"
            f"Accept: application/json\r\n"
            f"\r\n"
        )

    body = "".join(parts) + f"--{boundary}--\r\n"

    response = requests.post(
        config["url"] + "/api/data/v9.2/$batch",
        headers=headers,
        data=body,
    )
    response.raise_for_status()

    return _parse_batch_response(response, entity_names)


def _parse_batch_response(response: requests.Response, entity_names: List[str]) -> Mapping[str, Mapping[str, str]]:
    """Parse a $batch multipart response into per-entity DateTimeBehavior mappings."""
    content_type = response.headers.get("Content-Type", "")
    boundary_match = re.search(r"boundary=([^\s;]+)", content_type)
    if not boundary_match:
        logger.warning(
            "DateTimeBehavior batch response missing multipart boundary in Content-Type: %s. DateOnly detection will be skipped.",
            content_type,
        )
        return {}

    boundary = boundary_match.group(1).strip('"')
    parts = response.text.split(f"--{boundary}")

    result: dict[str, Mapping[str, str]] = {}
    entity_idx = 0

    for part in parts:
        stripped = part.strip()
        if not stripped or stripped == "--":
            continue
        if entity_idx >= len(entity_names):
            break

        # Each part: MIME headers \r\n\r\n HTTP status+headers \r\n\r\n body
        sections = re.split(r"(?:\r\n\r\n|\n\n)", part, maxsplit=2)
        if len(sections) < 3:
            entity_idx += 1
            continue

        json_body = sections[2].strip()
        if not json_body.startswith("{"):
            entity_idx += 1
            continue

        status_line = sections[1].strip().split("\r\n")[0] if sections[1].strip() else ""
        if " 200 " not in status_line and " 200\r" not in status_line:
            entity_name = entity_names[entity_idx] if entity_idx < len(entity_names) else "unknown"
            logger.warning(
                "Non-200 response in batch part for entity '%s': %s. DateOnly detection skipped for this entity.", entity_name, status_line
            )
            entity_idx += 1
            continue

        try:
            data = json.loads(json_body)
            behaviors: dict[str, str] = {}
            for attr in data.get("value", []):
                logical_name = attr.get("LogicalName", "")
                behavior_obj = attr.get("DateTimeBehavior")
                if behavior_obj and logical_name:
                    behaviors[logical_name] = behavior_obj.get("Value", "")
            result[entity_names[entity_idx]] = behaviors
        except (json.JSONDecodeError, KeyError):
            entity_name = entity_names[entity_idx] if entity_idx < len(entity_names) else "unknown"
            logger.warning("Failed to parse batch response for entity '%s'. DateOnly detection skipped for this entity.", entity_name)

        entity_idx += 1

    return result
