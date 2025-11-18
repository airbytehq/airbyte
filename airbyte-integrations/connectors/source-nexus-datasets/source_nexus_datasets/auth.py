# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import argparse
import collections
import datetime
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
from typing import Any, Mapping, Union
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse

import requests

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator, NoAuth
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.types import Config


HMAC = "HMAC_1"
EXPORT = "export"


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
        # self.logger.debug("user_detail_stream_attr: %s", user_detail_stream_attr)
        # self.logger.debug("path: %s", path)
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
        # self.logger.debug("def parseUrl : input_url: %s", self.input_url)
        # self.logger.debug("def actual path : dataset_path: %s", self.dataset_path)
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

        # self.logger.debug("parsedurl method url: %s", final_url)
        # self.logger.debug("parsedurl method path: %s", self.pathInfo)
        # self.logger.debug("parsedurl query string: %s", parsed_final_url.query)
        self.querystring = parsed_final_url.query

    def get_auth_header(self) -> Mapping[str, Any]:
        self.parseUrl()
        # self.actual_path=request_path
        signature = self.createAuthorizationHeader()

        custom_header_1 = self.dapi_date
        custom_header_2 = self.config.get("api_key", "")
        # self.logger.debug("Custom Headers 1: %s", custom_header_1)
        # self.logger.debug("Custom Headers 2: %s", custom_header_2)
        # self.logger.debug("Signature: %s", signature)
        # self.logger.debug("path info: %s", request_path)
        return {"Authorization": signature, "x-dapi-date": custom_header_1, "x-nexus-api-key": custom_header_2}

    def createAuthorizationHeader(self) -> str:
        signature = self.computeSignature()
        return f"HMAC_1 {self.accessKeyId}:{signature.decode()}:{self.userId}"

    def computeSignature(self) -> bytes:
        self.setDate()
        signingBase = self.createSigningBase()
        # self.logger.debug("The signingBase: %s", signingBase)
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
        self.dapi_date = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")

    def sign(self, signingBase: bytes) -> bytes:
        secret = self.secretAccessKey.encode("utf-8")
        hash = hmac.new(secret, signingBase, hashlib.sha256)
        return b64encode(hash.digest())
