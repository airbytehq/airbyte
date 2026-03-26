# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import hashlib
import hmac
import json
import logging
from base64 import b64encode
from collections import OrderedDict
from dataclasses import InitVar, dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Iterable, Mapping, Optional
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse

import requests

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.schema import SchemaLoader
from airbyte_cdk.sources.declarative.types import Config


DATASET_PATH = "rest/3.1/analytics/dataset"
EXPORT_PREFIX = "export"
DEFAULT_MODE = "Full"
DEFAULT_HTTP_METHOD = "GET"


@dataclass
class NexusCustomAuthenticator(DeclarativeAuthenticator):
    config: Config

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.config = config
        self.kwargs = kwargs
        self.logger = logging.getLogger("airbyte")

        # constants (removed from client config)
        self.dataset_path = DATASET_PATH
        self.export_prefix = EXPORT_PREFIX

        # user/config-driven values
        self.dataset_name = self.config.get("dataset_name", "")
        self.mode = self.config.get("mode", DEFAULT_MODE)
        self.input_url = self.config.get("base_url", "")

        # auth and request properties (snake_case)
        self.user_id = self.config.get("user_id", "")
        self.secret_access_key = self.config.get("secret_key", "")
        self.api_key = self.config.get("api_key", "")
        self.access_key_id = self.config.get("access_key_id", "")
        self.method = self.config.get("http_method", DEFAULT_HTTP_METHOD).upper()

        # optional payload support
        self.content_type = None
        self.payload = self.config.get("payload", "")
        self.file_content = None

        # computed during signing
        self.path_info = ""
        self.querystring = ""
        self.dapi_date = ""

    def parse_url(self) -> None:
        relative_path = "/".join([self.dataset_path, self.dataset_name, self.export_prefix])
        full_url = urljoin(self.input_url, relative_path)
        parsed_url = urlparse(full_url)

        query_params = {"mode": self.mode}
        existing_params = parse_qs(parsed_url.query)
        existing_params.update(query_params)

        new_query = urlencode(existing_params, doseq=True)
        final_url = urlunparse(parsed_url._replace(query=new_query))

        parsed_final_url = urlparse(final_url)
        self.path_info = parsed_final_url.path
        self.querystring = parsed_final_url.query

    def get_auth_header(self) -> Mapping[str, Any]:
        self.parse_url()
        signature = self.create_authorization_header()

        return {
            "Authorization": signature,
            "x-dapi-date": self.dapi_date,
            "x-nexus-api-key": self.api_key,
        }

    def create_authorization_header(self) -> str:
        signature = self.compute_signature()
        return f"HMAC_1 {self.access_key_id}:{signature.decode()}:{self.user_id}"

    def compute_signature(self) -> bytes:
        self.set_date()
        signing_base = self.create_signing_base()
        return self.sign(signing_base)

    def create_signing_base(self) -> bytes:
        path_info = self.path_info
        if self.querystring:
            path_info = f"{path_info}?{self.querystring}"

        components = OrderedDict(
            {
                "date": self.dapi_date.lower(),
                "method": self.method.lower(),
                "pathInfo": path_info.lower(),
                "payload": self.payload.lower() if self.payload else "",
                "content-type": self.content_type.lower() if self.payload and self.content_type else "",
            }
        )

        if self.file_content:
            components["file_content"] = self.file_content.decode("utf-8")

        signing_base = "".join(components.values())
        return signing_base.encode("utf-8")

    def set_date(self) -> None:
        self.dapi_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")

    def sign(self, signing_base: bytes) -> bytes:
        secret = self.secret_access_key.encode("utf-8")
        digest = hmac.new(secret, signing_base, hashlib.sha256).digest()
        return b64encode(digest)


@dataclass
class FlexibleDecoder(Decoder):
    """
    Decoder that parses JSONL-like responses based on Content-Type.
    """

    parameters: InitVar[Mapping[str, Any]] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self.logger = logging.getLogger("airbyte")

    def _convert_all_to_strings(self, obj: Any) -> Any:
        if obj is None:
            return None
        if isinstance(obj, (Decimal, datetime, date)):
            return str(obj)
        if isinstance(obj, dict):
            return {k: self._convert_all_to_strings(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._convert_all_to_strings(elem) for elem in obj]
        return str(obj)

    def decode(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        if response.status_code == 304:
            self.logger.error("Dataset is not ready, please contact infor member services")
            raise AirbyteTracedException(
                message="Dataset is not ready, please contact infor member services", failure_type=FailureType.config_error
            )
        if response.status_code == 202:
            self.logger.error("Dataset is not ready - try again later")
            raise AirbyteTracedException(message="Dataset is not ready, try again later", failure_type=FailureType.config_error)
        if response.status_code != 200:
            self.logger.error("Unexpected status code: %s", response.status_code)
            raise AirbyteTracedException(
                message=f"Unexpected status code: {response.status_code} please contact infor member services",
                failure_type=FailureType.config_error,
            )

        content_type = response.headers.get("Content-Type", "").lower()

        self.logger.info(f"[FlexibleDecoder] Response Content-Type: {content_type}")

        is_jsonl = any(
            ct in content_type
            for ct in (
                "application/json",
                "application/x-jsonlines",
                "application/x-jsonl+json",
                "application/jsonl",
                "application/octet-stream",  # ← ADD THIS — Infor Nexus data endpoint returns this
            )
        )

        if not is_jsonl:
            self.logger.error("Unsupported or unrecognized Content-Type: %s. Cannot decode response.", content_type)
            raise ValueError(f"Unsupported or unrecognized Content-Type: {content_type}")

        for line in response.content.decode("utf-8").splitlines():
            if not line.strip():
                continue
            try:
                record_dict = json.loads(line)
            except json.JSONDecodeError as exc:
                self.logger.warning("Skipping malformed JSONL line: %s - Error: %s", line.strip(), exc)
                continue
            processed_record = self._convert_all_to_strings(record_dict)
            yield processed_record

@dataclass
class DynamicSchemaLoader(SchemaLoader):
    """
    Fetches the schema dynamically from the Infor Nexus model metadata API.
    Called during `discover` — before any data sync.
    Endpoint: GET <base_url>/rest/3.1/Analytics/model/<dataset_name>/fetch
    Response: [{"name": "fieldName", "dataType": "String"}, ...]
    """

    config: Mapping[str, Any]
    parameters: InitVar[Mapping[str, Any]] = None

    _schema_cache: Optional[dict] = field(default=None, init=False)

    DATA_TYPE_MAP: Mapping[str, str] = field(default_factory=lambda: {
        "String":   "string",
        "string":   "string",
        "Text":     "string",
        "Char":     "string",
        "Integer":  "integer",
        "integer":  "integer",
        "Int":      "integer",
        "Long":     "integer",
        "Double":   "number",
        "Float":    "number",
        "Decimal":  "number",
        "decimal":  "number",
        "Boolean":  "boolean",
        "boolean":  "boolean",
        "Bool":     "boolean",
        "Date":     "string",
        "DateTime": "string",
        "Object":   "object",
        "Array":    "array",
    })

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self.logger = logging.getLogger("airbyte")

    def _get_auth_headers(self, url: str) -> Mapping[str, Any]:
        """
        Reuse NexusCustomAuthenticator's HMAC signing logic
        but override the URL path to point to the schema endpoint.
        """
        auth = NexusCustomAuthenticator(config=self.config)

        # Manually set the path for the schema endpoint
        # instead of calling parse_url() which builds the data endpoint path
        parsed = urlparse(url)
        auth.path_info = parsed.path
        auth.querystring = parsed.query

        # Compute signature using the schema endpoint path
        signature = auth.create_authorization_header()

        return {
            "Authorization": signature,
            "x-dapi-date": auth.dapi_date,
            "x-nexus-api-key": auth.api_key,
            "Content-Type": "application/json",
        }

    def get_json_schema(self) -> Mapping[str, Any]:
        if self._schema_cache:
            return self._schema_cache

        dataset_name = self.config.get("dataset_name", "")
        base_url = self.config.get("base_url", "").rstrip("/")

        url = f"{base_url}/rest/3.1/Analytics/model/PurchaseOrderTest/fetch"

        self.logger.info(f"Fetching schema from: {url}")

        try:
            headers = self._get_auth_headers(url)
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch schema from {url}: {e}")
            raise

        response_json = response.json()
        self.logger.info(f"Schema API raw response: {response_json}")

        # Navigate to the nested fields list: response -> data -> field
        data = response_json.get("data", {})
        fields = data.get("field", [])

        self.logger.info(f"Found {len(fields)} fields in schema response")

        properties = {}
        for f in fields:
            if not isinstance(f, dict):
                self.logger.warning(f"Skipping unexpected field entry: {f}")
                continue

            field_name = f.get("name")

            # No dataType in the response — default all fields to string // Still the change is in the RCTQ
            # If dataType appears in future, DATA_TYPE_MAP will handle it
            field_type = self.DATA_TYPE_MAP.get(f.get("dataType", ""), "string")

            if field_name:
                properties[field_name] = {"type": [field_type, "null"]}
                self.logger.info(f"Mapped field: {field_name} -> {field_type}")

        # Add known fields not returned by the schema API, this field does not exists in the schema but this is the change indicator field that is used by the connector to identify if the record is new or updated, this field is added as part of the decoder logic.
        properties["zzz_ChangeCode"] = {"type": ["string", "null"]}
        self._schema_cache = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "additionalProperties": True,
            "properties": properties,
        }

        self.logger.info(f"Schema loaded successfully with {len(properties)} fields.")
        return self._schema_cache