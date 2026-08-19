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
from typing import Any, ClassVar, Iterable, Mapping, Optional
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse

import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.schema import SchemaLoader
from airbyte_cdk.sources.declarative.types import Config
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


DATASET_PATH = "rest/3.1/analytics/dataset"
DATASET_METADATA_PATH = "rest/3.1/analytics/Dataset"
SCHEMA_PATH = "rest/3.1/Analytics/model"
EXPORT_PREFIX = "export"
DEFAULT_MODE = "Full"
DEFAULT_HTTP_METHOD = "GET"

# Injected by the connector — not returned by the Nexus schema API.
# Indicates whether a record is new or updated during incremental syncs.
INJECTED_FIELD_NAME = "zzz_ChangeCode"


@dataclass
class NexusCustomAuthenticator(DeclarativeAuthenticator):
    """
    Handles HMAC authentication for the Infor Nexus Data API.

    Every request is independently signed using a cryptographic hash of the
    request path, date, method, and payload. The resulting signature is
    submitted in the Authorization header.

    See: https://developer.infornexus.com/api/authentication-choices/hmac
    """

    config: Config

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.config = config
        self.kwargs = kwargs
        self.logger = logging.getLogger("airbyte")

        self.dataset_path = DATASET_PATH
        self.export_prefix = EXPORT_PREFIX

        self.dataset_name = self.config.get("dataset_name", "")
        self.mode = self.config.get("mode", DEFAULT_MODE)
        self.input_url = self.config.get("base_url", "")

        self.user_id = self.config.get("user_id", "")
        self.secret_access_key = self.config.get("secret_key", "")
        self.api_key = self.config.get("api_key", "")
        self.access_key_id = self.config.get("access_key_id", "")
        self.method = self.config.get("http_method", DEFAULT_HTTP_METHOD).upper()

        self.content_type = None
        self.payload = self.config.get("payload", "")
        self.file_content = None

        self.path_info = ""
        self.querystring = ""
        self.dapi_date = ""

    def parse_url(self) -> None:
        """Build the data endpoint URL and extract path and query components for signing."""
        relative_path = "/".join([self.dataset_path, self.dataset_name, self.export_prefix])
        full_url = urljoin(self.input_url, relative_path)
        parsed_url = urlparse(full_url)

        # Preserve any existing query params and append the mode param as a list
        # to keep consistent list-format values with parse_qs output.
        existing_params = parse_qs(parsed_url.query)
        existing_params["mode"] = [self.mode]

        new_query = urlencode(existing_params, doseq=True)
        final_url = urlunparse(parsed_url._replace(query=new_query))

        parsed_final_url = urlparse(final_url)
        self.path_info = parsed_final_url.path
        self.querystring = parsed_final_url.query

    def get_auth_header(self) -> Mapping[str, Any]:
        """Return signed auth headers for the data endpoint."""
        self.parse_url()
        return self._build_headers()

    def get_auth_header_for_path(self, path: str, querystring: str = "") -> Mapping[str, Any]:
        self.path_info = path
        self.querystring = querystring
        return self._build_headers()

    def _build_headers(self) -> Mapping[str, Any]:
        """Compute the HMAC signature and assemble the auth header dict."""
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
        digest = hmac.new(key=secret, msg=signing_base, digestmod=hashlib.sha256).digest()
        return b64encode(digest)


@dataclass
class FlexibleDecoder(Decoder):
    """
    Decodes JSONL-like responses from the Infor Nexus data endpoint.

    Handles the API's varied Content-Type headers (including
    application/octet-stream, which Infor Nexus uses for data responses)
    and converts all field values to strings for downstream compatibility.
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
            raise AirbyteTracedException(
                message="Dataset is not ready, please contact Infor member services.",
                failure_type=FailureType.config_error,
            )
        elif response.status_code == 202:
            raise AirbyteTracedException(
                message="Dataset is not ready — try again later.",
                failure_type=FailureType.config_error,
            )
        elif response.status_code != 200:
            raise AirbyteTracedException(
                message=(f"Unexpected status code {response.status_code}. Please contact Infor member services."),
                failure_type=FailureType.config_error,
            )

        content_type = response.headers.get("Content-Type", "").lower()
        response_url = (response.url or "").lower()
        self.logger.info("Response Content-Type: %s, URL: %s", content_type, response_url)

        file_format = self._detect_format(content_type, response_url)
        self.logger.info("Detected file format: %s", file_format)

        if file_format == "PARQUET":
            yield from self._decode_parquet(response)
        elif file_format == "CSV":
            yield from self._decode_csv(response)
        else:
            yield from self._decode_jsonl(response)

    def _detect_format(self, content_type: str, url: str) -> str:
        """Detect the response format from Content-Type header and URL."""
        if ".parquet" in url or "application/parquet" in content_type or "application/x-parquet" in content_type:
            return "PARQUET"
        elif ".csv" in url or "text/csv" in content_type:
            return "CSV"
        return "JSONL"

    def _decode_parquet(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        """Parquet is not supported in the manifest-only runtime environment."""
        raise AirbyteTracedException(
            message=(
                "Received Parquet data but this format is not supported by the Airbyte connector. "
                "Please configure the dataset export format to JSONL in Infor Nexus."
            ),
            failure_type=FailureType.config_error,
        )

    def _decode_csv(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        """CSV is not supported — configure the export to JSONL in Infor Nexus."""
        raise AirbyteTracedException(
            message=(
                "Received CSV data but this format is not supported by the Airbyte connector. "
                "Please configure the dataset export format to JSONL in Infor Nexus."
            ),
            failure_type=FailureType.config_error,
        )

    def _decode_jsonl(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        """Decode a JSONL (line-delimited JSON) response into records."""
        content_type = response.headers.get("Content-Type", "").lower()

        is_jsonl = any(
            ct in content_type
            for ct in (
                "application/json",
                "application/x-jsonlines",
                "application/x-jsonl+json",
                "application/jsonl",
                "application/octet-stream",
            )
        )

        if not is_jsonl:
            self.logger.error("Unsupported or unrecognized Content-Type: %s. Cannot decode response.", content_type)
            raise ValueError(f"Unsupported or unrecognized Content-Type: {content_type}")

        # Use the encoding declared by the response if available, fall back to
        # utf-8 with replacement to handle non-UTF-8 bytes (e.g. Latin-1 data).
        encoding = response.encoding or "utf-8"
        for line in response.content.decode(encoding, errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                record_dict = json.loads(line)
            except json.JSONDecodeError as exc:
                self.logger.warning("Skipping malformed JSONL line: %s — Error: %s", line.strip(), exc)
                continue
            yield self._convert_all_to_strings(record_dict)


@dataclass
class DynamicSchemaLoader(SchemaLoader):
    """
    Fetches the stream schema dynamically from the Infor Nexus model metadata API.

    Called during `discover` — before any data sync begins.
    Endpoint: GET <base_url>/rest/3.1/Analytics/model/<dataset_model_name>/fetch
    Response shape: {"data": {"field": [{"name": "fieldName", "dataType": "String"}, ...]}}

    An additional field (_nexus_ChangeCode) is injected into every schema to
    support incremental sync — it is not returned by the schema API but is
    present in data responses as a change indicator.
    """

    config: Mapping[str, Any]
    parameters: InitVar[Mapping[str, Any]] = None

    _schema_cache: Optional[dict] = field(default=None, init=False)

    DATA_TYPE_MAP: ClassVar[Mapping[str, Any]] = {
        "TEXT": {"type": ["string", "null"]},
        "PICKLIST": {"type": ["string", "null"]},
        "CHAR": {"type": ["string", "null"]},
        "VARCHAR": {"type": ["string", "null"]},
        "DATE": {"type": ["string", "null"], "format": "date"},
        "DATETIME": {"type": ["string", "null"], "format": "date-time"},
        "TIMESTAMP": {"type": ["string", "null"], "format": "date-time"},
        "INTEGER": {"type": ["integer", "null"]},
        "LONG": {"type": ["integer", "null"]},
        "DECIMAL": {"type": ["number", "null"]},
        "NUMERIC": {"type": ["number", "null"]},
        "FLOAT": {"type": ["number", "null"]},
        "DOUBLE": {"type": ["number", "null"]},
        "BOOLEAN": {"type": ["boolean", "null"]},
        "OBJECT": {"type": ["object", "null"]},
        "ARRAY": {"type": ["array", "null"]},
    }

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self.logger = logging.getLogger("airbyte")

    def _get_auth_headers(self, url: str) -> Mapping[str, Any]:
        """Sign a request to the given URL using the authenticator's public API."""
        auth = NexusCustomAuthenticator(config=self.config)
        parsed = urlparse(url)
        return auth.get_auth_header_for_path(
            path=parsed.path,
            querystring=parsed.query,
        )

    def _resolve_model_name(self) -> str:
        """
        Resolve the model name from the dataset metadata API.

        Calls GET <base_url>/rest/3.1/analytics/Dataset/<dataset_name> and extracts
        the model name from the `modelName` field (format: "ModelName:Self").
        """
        dataset_name = self.config.get("dataset_name", "")
        base_url = self.config.get("base_url", "").rstrip("/")
        url = f"{base_url}/{DATASET_METADATA_PATH}/{dataset_name}"

        self.logger.info("Resolving model name from dataset metadata: %s", url)

        try:
            headers = self._get_auth_headers(url)
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            raise AirbyteTracedException(
                message=(
                    f"Failed to resolve model name for dataset '{dataset_name}'. "
                    f"Could not fetch dataset metadata from Infor Nexus. Error: {exc}"
                ),
                failure_type=FailureType.config_error,
            ) from exc

        response_json = response.json()
        model_name_raw = response_json.get("modelName", "")

        if not model_name_raw:
            raise AirbyteTracedException(
                message=(
                    f"Dataset '{dataset_name}' metadata does not contain a 'modelName' field. "
                    "Please verify the dataset exists and is properly configured in Infor Nexus."
                ),
                failure_type=FailureType.config_error,
            )

        # modelName format is "ModelName:Self" — take the left side.
        model_name = model_name_raw.split(":")[0].strip()
        self.logger.info("Resolved model name: %s (from raw: %s)", model_name, model_name_raw)
        return model_name

    def get_json_schema(self) -> Mapping[str, Any]:
        # Return cached schema on subsequent calls — avoids redundant API requests.
        if self._schema_cache is not None:
            return self._schema_cache

        dataset_model_name = self._resolve_model_name()
        base_url = self.config.get("base_url", "").rstrip("/")
        url = f"{base_url}/{SCHEMA_PATH}/{dataset_model_name}/fetch"

        self.logger.info("Fetching schema from: %s", url)

        try:
            headers = self._get_auth_headers(url)
            response = requests.get(url, headers=headers)

            if response.status_code == 404:
                raise AirbyteTracedException(
                    message=(
                        f"Dataset Model Name '{dataset_model_name}' not found in Infor Nexus. "
                        "Please check the 'Dataset Model Name' in your connector configuration."
                    ),
                    failure_type=FailureType.config_error,
                )

            response.raise_for_status()

        except AirbyteTracedException:
            raise
        except requests.exceptions.RequestException as exc:
            raise AirbyteTracedException(
                message=(f"Failed to fetch schema for Dataset Model Name '{dataset_model_name}' from Infor Nexus. Error: {exc}"),
                failure_type=FailureType.system_error,
            ) from exc

        response_json = response.json()
        fields = response_json.get("data", {}).get("field", [])
        self.logger.info("Found %d fields in schema response.", len(fields))

        properties = {}
        for f in fields:
            if not isinstance(f, dict):
                self.logger.warning("Skipping unexpected field entry: %s", f)
                continue

            field_name = f.get("name")
            nexus_data_type = f.get("dataType", "")

            if field_name:
                # Fall back to string for any unmapped Nexus data types.
                properties[field_name] = self.DATA_TYPE_MAP.get(
                    nexus_data_type,
                    {"type": ["string", "null"]},
                )

        # Inject the change indicator field. Present in data responses but absent
        # from the schema API — used by the connector to detect new/updated records.
        properties[INJECTED_FIELD_NAME] = {"type": ["string", "null"]}

        self._schema_cache = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "additionalProperties": True,
            "properties": properties,
        }

        self.logger.info("Schema loaded successfully with %d fields.", len(properties))
        return self._schema_cache
