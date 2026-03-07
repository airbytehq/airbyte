# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import hashlib
import hmac
import json
import logging
from base64 import b64encode
from collections import OrderedDict
from dataclasses import InitVar, dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Iterable, Mapping
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse

import requests

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
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

        # optional payload support (kept as-is; only used if you later add payload signing)
        self.content_type = None
        self.payload = self.config.get("payload", "")
        self.file_content = None

        # computed during signing
        self.path_info = ""
        self.querystring = ""
        self.dapi_date = ""

    def parse_url(self) -> None:
        """
        Build the final request URL parts used in the signing base.
        Important: path + query must match what the requester sends.
        """
        relative_path = "/".join([self.dataset_path, self.dataset_name, self.export_prefix])
        full_url = urljoin(self.input_url, relative_path)
        parsed_url = urlparse(full_url)

        # Add required query params
        query_params = {"mode": self.mode}

        # Merge with existing query params, if any
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

        # Per your original logic: lowercase everything
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

    NOTE: This class currently yields `raw_data` as a JSON string.
    If you switch schema to `raw_data` as an object (recommended), change the yield to:
        yield {"raw_data": processed_record, "raw_data_string": json.dumps(processed_record)}
    and update manifest schema accordingly.
    """

    parameters: InitVar[Mapping[str, Any]] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self.logger = logging.getLogger("airbyte")

    def _convert_all_to_strings(self, obj: Any) -> Any:
        """
        Recursively converts all non-None values in a dictionary or list to strings.
        Handles Decimal, datetime.date, datetime.datetime, and other types.
        """
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
        # For 304 and 202 or not equal to 200 during data sync, raise/log with specific message
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

        is_jsonl = any(
            ct in content_type
            for ct in (
                "application/json",
                "application/x-jsonlines",
                "application/x-jsonl+json",
                "application/jsonl",
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
            yield {
                "raw_data": processed_record,
                "raw_data_string": json.dumps(processed_record),
            }
