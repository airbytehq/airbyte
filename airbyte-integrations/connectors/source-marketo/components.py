#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

"""Custom components for the Marketo source connector.

These components support the bulk export (async job) streams for Leads and
Activities, which require Marketo-specific creation/enqueue orchestration,
CSV parsing with null-byte filtering, dynamic schema discovery, and
per-activity-type stream generation.
"""

import csv
import io
import json
import logging
import re
from copy import deepcopy
from dataclasses import InitVar, dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Union

import dpath
import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.requesters import HttpRequester
from airbyte_cdk.sources.declarative.resolvers.components_resolver import (
    ComponentMappingDefinition,
    ComponentsResolver,
    ResolvedComponentMappingDefinition,
)
from airbyte_cdk.sources.declarative.retrievers.retriever import Retriever
from airbyte_cdk.sources.declarative.schema import SchemaLoader
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState
from airbyte_cdk.utils import AirbyteTracedException


logger = logging.getLogger("airbyte")


# ---------------------------------------------------------------------------
# Helper constants and functions (migrated from utils.py)
# ---------------------------------------------------------------------------

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
    """Convert camelCase/PascalCase Marketo field names to snake_case.

    Handles common abbreviations and special-case field names that the
    Marketo bulk-export API returns in activity attribute headers.
    """
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


def format_value(value: Any, schema: Mapping[str, Any]) -> Any:
    """Coerce a raw CSV string value to the type declared in *schema*."""
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


def _map_marketo_type(data_type: str) -> Mapping[str, Any]:
    """Map a Marketo field data type to a JSON Schema type definition."""
    if data_type == "date":
        field_schema: Dict[str, Any] = {"type": "string", "format": "date"}
    elif data_type == "datetime":
        field_schema = {"type": "string", "format": "date-time"}
    elif data_type in ("integer", "percent", "score"):
        field_schema = {"type": "integer"}
    elif data_type in ("float", "currency"):
        field_schema = {"type": "number"}
    elif data_type == "boolean":
        field_schema = {"type": "boolean"}
    elif data_type in STRING_TYPES:
        field_schema = {"type": "string"}
    elif data_type == "array":
        field_schema = {
            "type": "array",
            "items": {"type": ["integer", "number", "string", "null"]},
        }
    else:
        field_schema = {"type": "string"}

    # Make all fields nullable
    if isinstance(field_schema.get("type"), str):
        field_schema["type"] = [field_schema["type"], "null"]

    return field_schema


# ---------------------------------------------------------------------------
# Custom Requester: two-step create + enqueue for bulk export jobs
# ---------------------------------------------------------------------------


@dataclass
class MarketoBulkExportCreationRequester:
    """Creates and enqueues a Marketo bulk export job in a single ``send_request`` call.

    The Marketo bulk-export API requires two sequential POST calls:

    1. ``POST /bulk/v1/{entity}/export/create.json`` – creates the job and
       returns an ``exportId``.
    2. ``POST /bulk/v1/{entity}/export/{exportId}/enqueue.json`` – transitions
       the job from *Created* to *Queued* so that the server begins
       processing.

    This component wraps both steps behind the ``Requester.send_request``
    interface so that the CDK ``AsyncRetriever`` sees a single "creation"
    operation.
    """

    config: Config
    parameters: InitVar[Mapping[str, Any]]
    create_requester: HttpRequester
    enqueue_requester: HttpRequester
    include_fields_from_describe: Union[InterpolatedString, str, bool] = False

    _cached_fields: Optional[List[str]] = field(init=False, repr=False, default=None)

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._parameters = parameters
        if isinstance(self.include_fields_from_describe, (str, InterpolatedString)):
            self.include_fields_from_describe = str(self.include_fields_from_describe).lower() == "true"

    # -- Requester interface (only send_request is called by AsyncHttpJobRepository) --

    def send_request(
        self,
        stream_slice: Optional[StreamSlice] = None,
        stream_state: Optional[StreamState] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
        path: Optional[str] = None,
        request_headers: Optional[Mapping[str, Any]] = None,
        request_params: Optional[Mapping[str, Any]] = None,
        request_body_data: Optional[Union[Mapping[str, Any], str]] = None,
        request_body_json: Optional[Mapping[str, Any]] = None,
        log_formatter: Optional[Any] = None,
    ) -> Optional[requests.Response]:
        """Create a bulk export job and immediately enqueue it."""
        body = self._build_create_body(stream_slice)

        create_response = self.create_requester.send_request(
            stream_slice=stream_slice,
            request_body_json=body,
            log_formatter=log_formatter,
        )

        if not create_response:
            return None

        response_json = create_response.json()

        # Quota error 1029 is non-retryable
        self._check_quota_error(response_json, create_response.text)

        result = response_json.get("result")
        if not result:
            logger.warning(
                "No 'result' in export create response, returning as-is. Response: %s",
                create_response.text[:500],
            )
            return create_response

        export_id = result[0].get("exportId")
        status = result[0].get("status", "").lower()
        if status != "created" or not export_id:
            logger.warning("Unexpected export create status=%s exportId=%s", status, export_id)
            return create_response

        # Step 2: enqueue the job
        enqueue_slice = StreamSlice(
            partition=stream_slice.partition if stream_slice else {},
            cursor_slice=stream_slice.cursor_slice if stream_slice else {},
            extra_fields={
                **(stream_slice.extra_fields if stream_slice else {}),
                "export_id": export_id,
            },
        )
        self.enqueue_requester.send_request(
            stream_slice=enqueue_slice,
            log_formatter=log_formatter,
        )

        return create_response

    # -- Internal helpers --

    def _build_create_body(self, stream_slice: Optional[StreamSlice]) -> MutableMapping[str, Any]:
        body: MutableMapping[str, Any] = {"format": "CSV"}

        filter_params: MutableMapping[str, Any] = {}
        if stream_slice and stream_slice.cursor_slice:
            start_time = stream_slice.cursor_slice.get("start_time", "")
            end_time = stream_slice.cursor_slice.get("end_time", "")
            if start_time and end_time:
                filter_params["createdAt"] = {
                    "startAt": start_time,
                    "endAt": end_time,
                }

        # Activity type filter (set by DynamicDeclarativeStream partition)
        if stream_slice and stream_slice.partition:
            activity_type_id = stream_slice.partition.get("activity_type_id")
            if activity_type_id:
                filter_params["activityTypeIds"] = [int(activity_type_id)]

        if filter_params:
            body["filter"] = filter_params

        # For leads, include fields from the describe endpoint
        fields = self._get_export_fields()
        if fields:
            body["fields"] = fields

        return body

    def _get_export_fields(self) -> Optional[List[str]]:
        if not self.include_fields_from_describe:
            return None
        if self._cached_fields is not None:
            return self._cached_fields

        url_base = self.config["domain_url"].rstrip("/")
        auth_header = self.create_requester.get_authenticator().get_auth_header()

        try:
            resp = requests.get(
                f"{url_base}/rest/v1/leads/describe.json",
                headers=auth_header,
            )
            resp.raise_for_status()
            fields = []
            for record in resp.json().get("result", []):
                rest = record.get("rest")
                if rest and "name" in rest:
                    fields.append(rest["name"])
            self._cached_fields = fields
            return fields
        except (requests.RequestException, ValueError, KeyError):
            logger.warning("leads/describe.json request failed; omitting fields from export body")
            return None

    @staticmethod
    def _check_quota_error(response_json: Mapping[str, Any], response_text: str) -> None:
        errors = response_json.get("errors")
        if not errors:
            return
        error = errors[0]
        if error.get("code") == "1029" and re.match(r"Export daily quota \d+MB exceeded", error.get("message", "")):
            raise AirbyteTracedException(
                internal_message=response_text,
                message="Bulk export daily quota exceeded (resets at 12:00 AM CST).",
                failure_type=FailureType.config_error,
            )


# ---------------------------------------------------------------------------
# Custom CSV Decoder: filters null bytes before parsing
# ---------------------------------------------------------------------------


@dataclass
class MarketoCsvDecoder:
    """CSV decoder that strips null bytes and normalises ``"null"`` strings to ``None``."""

    config: Config
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._parameters = parameters

    def is_stream_response(self) -> bool:
        return False

    def decode(self, response: requests.Response) -> Iterable[MutableMapping[str, Any]]:
        response.encoding = "utf-8"
        text = response.text.replace("\x00", "")
        reader = csv.DictReader(io.StringIO(text))
        for row in reader:
            yield {k: (None if v in ("", "null") else v) for k, v in row.items()}


# ---------------------------------------------------------------------------
# Custom Record Transformation: flatten attributes + type coercion
# ---------------------------------------------------------------------------


@dataclass
class MarketoRecordTransformation(RecordTransformation):
    """Flatten the ``attributes`` JSON column and coerce values to schema types.

    Marketo bulk-export CSV rows may contain an ``attributes`` column whose
    value is a JSON object.  This transformation unpacks those nested
    key/value pairs into top-level record fields (applying ``clean_string``
    to normalise the key names) and then coerces every field value according
    to its declared JSON-Schema type.
    """

    config: Config
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._parameters = parameters

    def transform(
        self,
        record: MutableMapping[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        # Flatten the ``attributes`` JSON blob
        raw_attributes = record.pop("attributes", None)
        if raw_attributes and isinstance(raw_attributes, str):
            try:
                attributes = json.loads(raw_attributes)
            except (json.JSONDecodeError, ValueError):
                attributes = {}
        elif isinstance(raw_attributes, dict):
            attributes = raw_attributes
        else:
            attributes = {}

        for key, value in attributes.items():
            record[clean_string(key)] = value


# ---------------------------------------------------------------------------
# Custom Schema Loaders
# ---------------------------------------------------------------------------


@dataclass
class MarketoLeadsSchemaLoader(SchemaLoader):
    """Dynamic schema loader for the Leads stream.

    Merges the static ``leads.json`` schema with any custom fields
    discovered via the ``/rest/v1/leads/describe.json`` endpoint.
    """

    config: Config
    parameters: InitVar[Mapping[str, Any]]

    _schema: Optional[Mapping[str, Any]] = field(init=False, repr=False, default=None)

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._parameters = parameters

    def get_json_schema(self) -> Mapping[str, Any]:
        if self._schema is not None:
            return self._schema

        import pathlib

        # Load static schema from source_marketo/schemas/leads.json
        schema_path = pathlib.Path(__file__).parent / "source_marketo" / "schemas" / "leads.json"
        if schema_path.exists():
            static_schema = json.loads(schema_path.read_text())
        else:
            static_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": ["null", "object"],
                "additionalProperties": True,
                "properties": {},
            }

        properties = dict(static_schema.get("properties", {}))

        # Fetch custom fields from describe endpoint
        available = self._fetch_describe_fields()
        for field_name, data_type in available.items():
            if field_name not in properties:
                properties[field_name] = _map_marketo_type(data_type)

        self._schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": ["null", "object"],
            "additionalProperties": True,
            "properties": properties,
        }
        return self._schema

    def _fetch_describe_fields(self) -> Mapping[str, str]:
        url_base = self.config["domain_url"].rstrip("/")
        try:
            # Build auth header – reuse the OAuth token from config if available
            token = self._get_access_token()
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            resp = requests.get(f"{url_base}/rest/v1/leads/describe.json", headers=headers)
            resp.raise_for_status()
            fields: Dict[str, str] = {}
            for record in resp.json().get("result", []):
                rest = record.get("rest")
                if rest and "name" in rest:
                    fields[rest["name"]] = record.get("dataType", "string")
            return fields
        except (requests.RequestException, ValueError, KeyError):
            logger.warning("leads/describe.json request failed; using static schema only")
            return {}

    def _get_access_token(self) -> Optional[str]:
        url_base = self.config["domain_url"].rstrip("/")
        try:
            resp = requests.get(
                f"{url_base}/identity/oauth/token",
                params={
                    "grant_type": "client_credentials",
                    "client_id": self.config["client_id"],
                    "client_secret": self.config["client_secret"],
                },
            )
            resp.raise_for_status()
            return resp.json().get("access_token")
        except (requests.RequestException, ValueError, KeyError):
            logger.warning("OAuth token request failed for schema loader")
            return None


@dataclass
class MarketoActivitySchemaLoader(SchemaLoader):
    """Dynamic schema loader for individual Activity streams.

    Receives the activity type metadata (including ``attributes``) via
    ``$parameters`` and builds the JSON schema from the attribute list.
    """

    config: Config
    parameters: InitVar[Mapping[str, Any]]
    activity_attributes: Optional[str] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._parameters = parameters
        if self.activity_attributes and isinstance(self.activity_attributes, str):
            try:
                self._attributes = json.loads(self.activity_attributes)
            except (json.JSONDecodeError, ValueError):
                self._attributes = []
        elif isinstance(self.activity_attributes, list):
            self._attributes = self.activity_attributes
        else:
            self._attributes = []

    def get_json_schema(self) -> Mapping[str, Any]:
        properties: Dict[str, Any] = {
            "marketoGUID": {"type": ["null", "string"]},
            "leadId": {"type": ["null", "integer"]},
            "activityDate": {"type": ["null", "string"], "format": "date-time"},
            "activityTypeId": {"type": ["null", "integer"]},
            "campaignId": {"type": ["null", "integer"]},
            "primaryAttributeValueId": {"type": ["null", "string"]},
            "primaryAttributeValue": {"type": ["null", "string"]},
        }

        for attr in self._attributes:
            attr_name = clean_string(attr.get("name", ""))
            if not attr_name:
                continue
            properties[attr_name] = _map_marketo_type(attr.get("dataType", "string"))

        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": ["null", "object"],
            "additionalProperties": True,
            "properties": properties,
        }


# ---------------------------------------------------------------------------
# Custom Components Resolver: per-activity-type stream generation
# ---------------------------------------------------------------------------


@dataclass
class MarketoActivitiesComponentsResolver(ComponentsResolver):
    """Resolves activity-type metadata into per-type stream configurations.

    Fetches the ``/rest/v1/activities/types.json`` endpoint and yields one
    resolved stream template per activity type, mapping:

    * ``stream_name``  -> ``activities_{clean_string(name)}``
    * ``activity_type_id`` -> the numeric Marketo activity-type ID
    * ``activity_attributes`` -> JSON-encoded attribute list for the schema loader
    """

    retriever: Retriever
    config: Config
    components_mapping: List[ComponentMappingDefinition]
    parameters: InitVar[Mapping[str, Any]]

    _resolved_components: List[ResolvedComponentMappingDefinition] = field(init=False, repr=False, default_factory=list)

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        for component_mapping in self.components_mapping:
            if isinstance(component_mapping.value, (str, InterpolatedString)):
                interpolated_value = (
                    InterpolatedString.create(component_mapping.value, parameters=parameters)
                    if isinstance(component_mapping.value, str)
                    else component_mapping.value
                )

                field_path = [InterpolatedString.create(path, parameters=parameters) for path in component_mapping.field_path]

                self._resolved_components.append(
                    ResolvedComponentMappingDefinition(
                        field_path=field_path,
                        value=interpolated_value,
                        value_type=component_mapping.value_type,
                        parameters=parameters,
                    )
                )
            else:
                raise ValueError(f"Expected a string or InterpolatedString for value in mapping: {component_mapping}")

    def resolve_components(self, stream_template_config: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
        kwargs = {"stream_template_config": stream_template_config}

        for stream_slice in self.retriever.stream_slices():
            for components_values in self.retriever.read_records(records_schema={}, stream_slice=stream_slice):
                updated_config = deepcopy(stream_template_config)

                # Enrich components_values with computed fields
                raw_name = components_values.get("name", "")
                enriched: Dict[str, Any] = dict(components_values)
                enriched["stream_name"] = f"activities_{clean_string(raw_name)}"
                enriched["activity_attributes_json"] = json.dumps(components_values.get("attributes", []))

                kwargs["components_values"] = enriched
                kwargs["stream_slice"] = stream_slice

                for resolved_component in self._resolved_components:
                    valid_types = (resolved_component.value_type,) if resolved_component.value_type else None
                    value = resolved_component.value.eval(self.config, valid_types=valid_types, **kwargs)

                    path = [p.eval(self.config, **kwargs) for p in resolved_component.field_path]
                    dpath.set(updated_config, path, value)

                yield updated_config
