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
from typing import Any, Iterable, Mapping, Union
from urllib.parse import urlparse

import requests

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.types import Config


@dataclass
class NexusCustomAuthenticator(DeclarativeAuthenticator):
    config: Config
    parameters: InitVar[Mapping[str, Any]] = None

    def __init__(self, config: Mapping[str, Any], parameters: Mapping[str, Any] = None, *kwargs):
        super().__init__()
        self.config = config
        self.parameters = parameters or {}
        self.logger = logging.getLogger("airbyte")
        self.logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)

        self.userId = self.config.get("user_id", "")
        self.secretAccessKey = self.config.get("secret_key", "")
        self.method = self.config.get("http_method", "GET").upper()
        self.accessKeyId = self.config.get("access_key_id", "")
        self.contentType = None  # Only set if payload exists
        self.payload = self.config.get("payload", "")
        self.fileContent = None  # Add file content here if required
        self.pathInfo = ""
        self.querystring = ""
        self.dapi_date = ""
        self.url_base = self.parameters.get("url_base", "")
        self.logger.debug(f"Parameters received: {self.parameters}")
        self.logger.debug(f"Config: {self.config}")
        self.logger.debug(f"url_base before interpolation: {self.url_base}")

        # Interpolate the url_base using config
        for key, value in self.config.items():
            placeholder = f"{{{{ config['{key}'] }}}}"
            self.url_base = self.url_base.replace(placeholder, str(value))

        self.logger.debug(f"url_base after interpolation: {self.url_base}")

    def parse_url(self):
        parsed_final_url = urlparse(self.url_base)
        self.pathInfo = parsed_final_url.path
        self.querystring = parsed_final_url.query

    # Entry point for getting auth headers, called by the Declarative framework
    def get_auth_header(self) -> Mapping[str, Any]:
        self.parse_url()
        signature = self.create_authorization_header()

        custom_header_1 = self.dapi_date
        custom_header_2 = self.config.get("api_key", "")
        return {"Authorization": signature, "x-dapi-date": custom_header_1, "x-nexus-api-key": custom_header_2}

    def create_authorization_header(self) -> str:
        signature = self.compute_signature()
        return f"HMAC_1 {self.accessKeyId}:{signature.decode()}:{self.userId}"

    def compute_signature(self) -> bytes:
        self.set_date()
        signingBase = self.create_signing_base()
        return self.sign(signingBase)

    def create_signing_base(self) -> bytes:
        if self.querystring:
            self.pathInfo += f"?{self.querystring}"
        # self.logger.debug("signingBase pathInfo: %s", self.pathInfo)
        ##To create signing base, all should be in lowercase
        components = OrderedDict(
            {
                "date": self.dapi_date.lower(),
                "method": self.method.lower(),  ## Think about this
                "pathInfo": self.pathInfo.lower(),  # Use dynamic path
                "payload": self.payload.lower() if self.payload else "",
                "content-type": self.contentType.lower() if self.payload and self.contentType else "",
            }
        )

        if self.fileContent:
            components["file_content"] = self.fileContent.decode("utf-8")

        signingBase = "".join(components.values())
        return signingBase.encode("utf-8")

    def set_date(self):
        self.dapi_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")

    def sign(self, signingBase: bytes) -> bytes:
        secret = self.secretAccessKey.encode("utf-8")
        hash = hmac.new(secret, signingBase, hashlib.sha256)
        return b64encode(hash.digest())


@dataclass  # Use the dataclass decorator
class FlexibleDecoder(Decoder):
    """
    A custom decoder that dynamically selects the appropriate underlying decoder
    (JSONL, CSV, or Parquet) based on the 'Content-Type' header of the HTTP response.
    CSV parsing options are hardcoded within this class.
    This version assumes files are NOT gzipped.
    """

    def __post_init__(self):
        self.logger = logging.getLogger("airbyte")
        self.logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)

    def convert_all_to_strings(self, obj: Any) -> Any:
        """
        Recursively converts all non-None values in a dictionary or list to strings.
        This handles Decimal, datetime.date, datetime.datetime, and other types.
        """
        if obj is None:
            return None
        elif isinstance(obj, (Decimal, datetime, date)):
            return str(obj)  # Convert Decimal, datetime, date to string
        elif isinstance(obj, dict):
            return {k: self.convert_all_to_strings(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_all_to_strings(elem) for elem in obj]
        # For other primitive types (int, float, bool, string already), convert to string
        # This ensures consistency, even if it means converting a string to a string.
        # This is the safest approach for dynamic schemaless sources to Parquet.
        return str(obj)

    def decode(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        """
        Decodes the raw response body from the requests.Response object based on its Content-Type header.
        Args:
            response (requests.Response): The HTTP response object from the request.
        Returns:
            Iterable[Mapping[str, Any]]: An iterable of decoded records (dictionaries).
        """
        # For 304 and 202 during data sync, raise error with specific message
        if response.status_code == 304:
            self.logger.error("Data set is not ready, check the source")
            raise ValueError("Data set is not ready, check the source")
            return
        elif response.status_code == 202:
            self.logger.error("Dataset is not Ready - Try again later")
        elif response.status_code not in (200, 304, 202):
            # Log but don't fail on other unexpected status codes - allow graceful handling
            self.logger.error(f"Unexpected status code: {response.status_code}")
            return

        content_type = response.headers.get("Content-Type", "").lower()
        content_bytes = response.content

        if (
            "application/json" in content_type
            or "application/x-jsonlines" in content_type
            or "application/x-jsonl+json" in content_type
            or "application/jsonl" in content_type
        ):
            for line in content_bytes.decode("utf-8").splitlines():
                if line.strip():
                    try:
                        record_dict = json.loads(line)
                        # Convert all values within the record to strings
                        processed_record = self.convert_all_to_strings(record_dict)
                        # Yield the entire processed record as a JSON string under a single key
                        yield {"raw_data": json.dumps(processed_record)}
                    except json.JSONDecodeError as e:
                        logging.warning(f"Skipping malformed JSONL line: {line.strip()} - Error: {e}")
        else:
            self.logger.error(f"Unsupported or unrecognized Content-Type: {content_type}. Cannot decode response.")
            raise ValueError(f"Unsupported or unrecognized Content-Type: {content_type}")
