#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import hashlib
import hmac
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping
from urllib.parse import urlencode

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.types import Config


@dataclass
class AmazonSQSAuthenticator(DeclarativeAuthenticator):
    config: Config

    def __post_init__(self):

        self.AWS_ACCESS_KEY_ID = self.config.get("access_key")
        self.AWS_SECRET_ACCESS_KEY = self.config.get("secret_key")
        self.REGION_NAME = self.config.get("region")
        self.QUEUE_URL = self.config.get("queue_url")

        self.service = "sqs"
        self.service_url = f"sqs.{self.REGION_NAME}.amazonaws.com"
        self.path = "/"

        self.algorithm = "AWS4-HMAC-SHA256"
        self.signed_headers = "host;x-amz-date"

        self.params = {
            "Action": "ReceiveMessage",
            "MessageAttributeNames": self.config.get("attributes_to_return").split(","),
            "QueueUrl": self.config.get("queue_url"),
            "VisibilityTimeout": self.config.get("visibility_timeout"),
            "WaitTimeSeconds": self.config.get("max_wait_time"),
        }
        self.query_string = urlencode(self.params)

        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-amz-json-1.1",
            "Host": f"sqs.{self.REGION_NAME}.amazonaws.com",
        }

        self.payload_hash = hashlib.sha256(("").encode()).hexdigest()

    def get_auth_header(self) -> Mapping[str, Any]:
        """The header to set on outgoing HTTP requests"""

        date_time_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

        canonical_headers = f"host:{self.service_url}\nx-amz-date:{date_time_stamp}\n"
        canonical_request = (
            "GET" + "\n" + "/" + "\n" + self.query_string + "\n" + canonical_headers + "\n" + self.signed_headers + "\n" + self.payload_hash
        )

        date_stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
        credential_scope = f"{date_stamp}/{self.REGION_NAME}/{self.service}/aws4_request"
        string_to_sign = (
            self.algorithm
            + "\n"
            + date_time_stamp
            + "\n"
            + credential_scope
            + "\n"
            + hashlib.sha256(canonical_request.encode()).hexdigest()
        )

        signing_key = self.get_signature_key(date_stamp)
        signature = hmac.new(signing_key, string_to_sign.encode(), hashlib.sha256).hexdigest()

        authorization_header = (
            self.algorithm + f" Credential={self.AWS_ACCESS_KEY_ID}/{credential_scope}," + f" SignedHeaders={self.signed_headers},"
            f" Signature={signature}"
        )

        self.headers.update({"x-amz-date": date_time_stamp, "Authorization": authorization_header})
        return self.headers

    def get_signature_key(self, date_stamp):
        k_date = self.sign((f"AWS4{self.AWS_SECRET_ACCESS_KEY}").encode(), date_stamp)
        k_region = self.sign(k_date, self.REGION_NAME)
        k_service = self.sign(k_region, self.service)
        k_signing = self.sign(k_service, "aws4_request")
        return k_signing

    def sign(self, key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def get_request_params(self) -> Mapping[str, Any]:
        """HTTP request parameter to add to the requests"""
        return self.params
