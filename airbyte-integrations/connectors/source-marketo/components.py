#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
import logging
import re
from dataclasses import InitVar, dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Union

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.decoders import Decoder, JsonDecoder
from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_protocol.models import FailureType

logger = logging.getLogger("airbyte")

STRING_TYPES = [
    "string",
    "email",
    "reference",
    "url",
    "phone",
    "textarea",
    "text",
    "lead_function",
]


def clean_string(string: str) -> str:
    fix = {
        "api method name": "Api Method Name",
        "modifying user": "Modifying User",
        "request id": "Request Id",
    }
    string = fix.get(string, string)
    abbreviations = ("URL", "GUID", "IP", "ID", "IDs", "API", "SFDC", "CRM", "SLA")
    if any(map(lambda w: w in string.split(), abbreviations)):
        return string.lower().replace(" ", "_")
    return "".join("_" + c.lower() if c.isupper() else c for c in string if c != " ").strip("_")


def format_value(value, schema):
    if not isinstance(schema["type"], list):
        field_type = [schema["type"]]
    else:
        field_type = schema["type"]

    if value in [None, "", "null"]:
        return None
    elif "integer" in field_type:
        if isinstance(value, int):
            return value
        try:
            decimal_index = value.find(".")
            if decimal_index > 0:
                value = value[:decimal_index]
            return int(value)
        except (ValueError, TypeError, AttributeError):
            return None
    elif "string" in field_type:
        return str(value)
    elif "number" in field_type:
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    elif "boolean" in field_type:
        if isinstance(value, bool):
            return value
        return value.lower() == "true"

    return value


def marketo_data_type_to_json_schema(data_type: str) -> Mapping[str, Any]:
    if data_type == "date":
        return {"type": ["null", "string"], "format": "date"}
    elif data_type == "datetime":
        return {"type": ["null", "string"], "format": "date-time"}
    elif data_type in ["integer", "percent", "score"]:
        return {"type": ["null", "integer"]}
    elif data_type in ["float", "currency"]:
        return {"type": ["null", "number"]}
    elif data_type == "boolean":
        return {"type": ["null", "boolean"]}
    elif data_type in STRING_TYPES:
        return {"type": ["null", "string"]}
    elif data_type in ["array"]:
        return {"type": ["null", "array"], "items": {"type": ["integer", "number", "string", "null"]}}
    else:
        return {"type": ["null", "string"]}


@dataclass
class MarketoBulkExportStatusExtractor(RecordExtractor):
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    resource_name: str = ""
    decoder: Decoder = field(default_factory=lambda: JsonDecoder(parameters={}))

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._parameters = parameters

    def extract_records(self, response: requests.Response) -> Iterable[Any]:
        result = response.json().get("result", [])
        if not result:
            return

        status = result[0].get("status", "")

        if status == "Created":
            export_id = result[0].get("exportId", "")
            base_url = self.config["domain_url"].rstrip("/")
            enqueue_url = f"{base_url}/bulk/v1/{self.resource_name}/export/{export_id}/enqueue.json"
            auth_header = response.request.headers.get("Authorization", "")
            enqueue_resp = requests.post(enqueue_url, headers={"Authorization": auth_header})
            enqueue_result = enqueue_resp.json().get("result", [])
            if enqueue_result:
                yield enqueue_result[0].get("status", "Queued")
            else:
                yield "Queued"
        else:
            yield status


@dataclass
class MarketoBulkExportErrorHandler:
    config: Config
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._parameters = parameters

    @staticmethod
    def check_for_quota_error(response: requests.Response) -> None:
        if errors := response.json().get("errors"):
            if errors[0].get("code") == "1029" and re.match(
                r"Export daily quota \d+MB exceeded", errors[0].get("message", "")
            ):
                message = "Daily limit for job extractions has been reached (resets daily at 12:00AM CST)."
                raise AirbyteTracedException(
                    internal_message=response.text,
                    message=message,
                    failure_type=FailureType.config_error,
                )


@dataclass
class MarketoCsvTransformation(RecordTransformation):
    config: Config
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._parameters = parameters

    def transform(
        self,
        record: Dict[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        attributes_str = record.pop("attributes", None)
        if attributes_str and isinstance(attributes_str, str):
            try:
                attributes = json.loads(attributes_str)
                for key, value in attributes.items():
                    record[clean_string(key)] = value
            except (json.JSONDecodeError, TypeError):
                pass

        for key in list(record.keys()):
            if record[key] in ("", "null"):
                record[key] = None


@dataclass
class MarketoLeadsSchemaLoader(SchemaLoader):
    config: Config
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._parameters = parameters

    def _get_auth_token(self) -> str:
        base_url = self.config["domain_url"].rstrip("/")
        token_url = f"{base_url}/identity/oauth/token"
        resp = requests.get(
            token_url,
            params={
                "grant_type": "client_credentials",
                "client_id": self.config["client_id"],
                "client_secret": self.config["client_secret"],
            },
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

    def get_json_schema(self) -> Mapping[str, Any]:
        base_url = self.config["domain_url"].rstrip("/")
        token = self._get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}

        describe_url = f"{base_url}/rest/v1/leads/describe.json"
        resp = requests.get(describe_url, headers=headers)
        resp.raise_for_status()

        properties: MutableMapping[str, Any] = {}
        result = resp.json().get("result", [])
        for field_desc in result:
            rest = field_desc.get("rest")
            if not rest or "name" not in rest:
                continue

            field_name = rest["name"]
            data_type = field_desc.get("dataType", "string")
            properties[field_name] = marketo_data_type_to_json_schema(data_type)

        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": ["null", "object"],
            "additionalProperties": True,
            "properties": properties,
        }


@dataclass
class MarketoActivitySchemaLoader(SchemaLoader):
    config: Config
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._parameters = parameters
        self._activity_type_id = str(parameters.get("activity_type_id", ""))

    def _get_auth_token(self) -> str:
        base_url = self.config["domain_url"].rstrip("/")
        token_url = f"{base_url}/identity/oauth/token"
        resp = requests.get(
            token_url,
            params={
                "grant_type": "client_credentials",
                "client_id": self.config["client_id"],
                "client_secret": self.config["client_secret"],
            },
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

    def get_json_schema(self) -> Mapping[str, Any]:
        properties: MutableMapping[str, Any] = {
            "marketoGUID": {"type": ["null", "string"]},
            "leadId": {"type": ["null", "integer"]},
            "activityDate": {"type": ["null", "string"], "format": "date-time"},
            "activityTypeId": {"type": ["null", "integer"]},
            "campaignId": {"type": ["null", "integer"]},
            "primaryAttributeValueId": {"type": ["null", "string"]},
            "primaryAttributeValue": {"type": ["null", "string"]},
        }

        if self._activity_type_id:
            try:
                base_url = self.config["domain_url"].rstrip("/")
                token = self._get_auth_token()
                headers = {"Authorization": f"Bearer {token}"}
                resp = requests.get(
                    f"{base_url}/rest/v1/activities/types.json",
                    headers=headers,
                )
                resp.raise_for_status()
                for activity_type in resp.json().get("result", []):
                    if str(activity_type.get("id")) == self._activity_type_id:
                        for attr in activity_type.get("attributes", []):
                            attr_name = clean_string(attr.get("name", ""))
                            data_type = attr.get("dataType", "string")
                            if attr_name:
                                properties[attr_name] = marketo_data_type_to_json_schema(data_type)
                        break
            except Exception as e:
                logger.warning(f"Failed to fetch activity type schema for type {self._activity_type_id}: {e}")

        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": ["null", "object"],
            "additionalProperties": True,
            "properties": properties,
        }
