# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import argparse
import collections
import csv
import hashlib
import hmac
import io
import json
import logging
import string
import sys
import time
import urllib
from base64 import b64encode
from collections import OrderedDict
from dataclasses import InitVar, dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Iterable, Mapping, Union
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse

import pandas as pd

# import pyarrow.parquet as pq
import requests

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator, NoAuth
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.types import Config


HMAC = "HMAC_1"


@dataclass
class NexusCustomAuthenticator(DeclarativeAuthenticator):
    config: Config

    def __init__(self, config: Mapping[str, Any], *kwargs):
        super().__init__()
        self.config = config
        self.kwargs = kwargs
        self.logger = logging.getLogger("airbyte")
        self.logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)

        user_detail_stream_attr = self.config.get("datasets_stream", {})
        path = user_detail_stream_attr.get("parameters", {})
        self.dataset_path = self.config.get("dataset_path", "")
        self.dataset_name = self.config.get("dataset_name", "")
        self.export_prefix = self.config.get("dataset_export_prefix", "")
        self.mode = self.config.get("mode", "")
        self.input_url = self.config.get("base_url", "")
        self.userId = self.config.get("user_id", "")
        self.secretAccessKey = self.config.get("secret_key", "")
        self.dataKey = self.config.get("api_key", "")
        self.method = self.config.get("http_method", "GET").upper()
        self.accessKeyId = self.config.get("access_key_id", "")
        self.contentType = None  # Only set if payload exists
        self.payload = self.config.get("payload", "")
        self.fileContent = None  # Add file content here if required
        self.pathInfo = ""
        self.querystring = ""
        self.dapi_date = ""

    def parseUrl(self):
        relative_path = "/".join([self.dataset_path, self.dataset_name, self.export_prefix])
        full_url = urljoin(self.input_url, relative_path)
        parsedUrl = urlparse(full_url)

        # Optional: Add your query parameters here
        query_params = {"mode": self.mode}

        # If existing query parameters exist, merge them
        existing_params = parse_qs(parsedUrl.query)
        existing_params.update(query_params)

        # Convert the query parameters to a string
        new_query = urlencode(existing_params, doseq=True)

        # Build the final URL with the updated query string
        final_url = urlunparse(parsedUrl._replace(query=new_query))

        # Parse final_url to extract components like path
        parsed_final_url = urlparse(final_url)
        self.pathInfo = parsed_final_url.path
        self.querystring = parsed_final_url.query

    def get_auth_header(self) -> Mapping[str, Any]:
        self.parseUrl()
        signature = self.createAuthorizationHeader()

        custom_header_1 = self.dapi_date
        custom_header_2 = self.config.get("api_key", "")
        return {"Authorization": signature, "x-dapi-date": custom_header_1, "x-nexus-api-key": custom_header_2}

    def createAuthorizationHeader(self) -> str:
        signature = self.computeSignature()
        return f"HMAC_1 {self.accessKeyId}:{signature.decode()}:{self.userId}"

    def computeSignature(self) -> bytes:
        self.setDate()
        signingBase = self.createSigningBase()
        return self.sign(signingBase)

    def createSigningBase(self) -> bytes:
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

    def setDate(self):
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

    parameters: InitVar[Mapping[str, Any]] = None  # Capture any other parameters from manifest

    # CSV parsing options are hardcoded as class attributes or set in __post_init__
    _csv_delimiter: str = ","
    _csv_quote_char: str = '"'
    _csv_encoding: str = "utf-8"
    _csv_skip_rows_before_header: int = 0

    def __post_init__(self, parameters: Mapping[str, Any]):
        self.logger = logging.getLogger("airbyte")
        self.logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)
        pass

    def _convert_all_to_strings(self, obj: Any) -> Any:
        """
        Recursively converts all non-None values in a dictionary or list to strings.
        This handles Decimal, datetime.date, datetime.datetime, and other types.
        """
        if obj is None:
            return None
        elif isinstance(obj, (Decimal, datetime, date)):
            return str(obj)  # Convert Decimal, datetime, date to string
        elif isinstance(obj, dict):
            return {k: self._convert_all_to_strings(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_all_to_strings(elem) for elem in obj]
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
                        processed_record = self._convert_all_to_strings(record_dict)
                        # Yield the entire processed record as a JSON string under a single key
                        yield {"raw_data": json.dumps(processed_record)}
                    except json.JSONDecodeError as e:
                        logging.warning(f"Skipping malformed JSONL line: {line.strip()} - Error: {e}")
        else:
            self.logger.error(f"Unsupported or unrecognized Content-Type: {content_type}. Cannot decode response.")
            raise ValueError(f"Unsupported or unrecognized Content-Type: {content_type}")
