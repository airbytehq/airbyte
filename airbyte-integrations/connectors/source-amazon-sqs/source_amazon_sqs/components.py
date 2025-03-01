#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import datetime
import hashlib
import hmac
import json
from dataclasses import dataclass
from typing import Any, Mapping, Union
from urllib.parse import urlparse

import requests

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import NoAuth
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.types import Config


@dataclass
class CustomAuthenticator(NoAuth):
    config: Config
    access_key: Union[InterpolatedString, str]
    secret_key: Union[InterpolatedString, str]
    region: Union[InterpolatedString, str]
    attributes_to_return: Union[InterpolatedString, str]
    queue_url: Union[InterpolatedString, str]
    visibility_timeout: Union[InterpolatedString, str]
    max_wait_time: Union[InterpolatedString, str]
    target: Union[InterpolatedString, str]

    def __post_init__(self, parameters: Mapping[str, Any]):
        self._access_key = InterpolatedString.create(self.access_key, parameters=parameters).eval(self.config)
        self._secret_key = InterpolatedString.create(self.secret_key, parameters=parameters).eval(self.config)
        self._region = InterpolatedString.create(self.region, parameters=parameters).eval(self.config)
        self._attributes_to_return = InterpolatedString.create(self.attributes_to_return, parameters=parameters).eval(self.config)
        self._queue_url = InterpolatedString.create(self.queue_url, parameters=parameters).eval(self.config)
        self._visibility_timeout = InterpolatedString.create(self.visibility_timeout, parameters=parameters).eval(self.config)
        self._max_wait_time = InterpolatedString.create(self.max_wait_time, parameters=parameters).eval(self.config)
        self._target = InterpolatedString.create(self.target, parameters=parameters).eval(self.config)
        self.service = "sqs"

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        """Attach the HTTP headers, body and sign the SQS request."""
        self.headers = {
            "Content-Type": "application/x-amz-json-1.0",
            "Host": f"sqs.{self._region}.amazonaws.com",
            "X-Amz-Target": f"AmazonSQS.{self._target}",
        }

        payload = {
            "QueueUrl": self._queue_url,
            "AttributeNames": self._attributes_to_return.split(",") if self._attributes_to_return else ["All"],
            "MaxNumberOfMessages": self._visibility_timeout,
            "VisibilityTimeout": self._max_wait_time,
        }

        try:
            body_json = json.loads(request.body.decode("utf-8")) if request.body else {}
        except json.JSONDecodeError as e:
            body_json = {}
        body_json["QueueUrl"] = payload["QueueUrl"]
        body_json["AttributeNames"] = payload["AttributeNames"]
        body_json["VisibilityTimeout"] = payload["MaxNumberOfMessages"]
        body_json["WaitTimeSeconds"] = payload["VisibilityTimeout"]

        request.body = json.dumps(body_json).encode("utf-8")

        # Sign the AWS request
        authorization_header, amz_date = self.sign_request(
            self.service,
            self._region,
            request.method,
            request.url,
            self.headers,
            body_json,
            self._access_key,
            self._secret_key,
        )
        self.headers["X-Amz-Date"] = amz_date
        self.headers["Authorization"] = authorization_header
        self.headers["Content-Length"] = str(len(json.dumps(payload)))
        request.headers.update(self.headers)
        return request

    @property
    def auth_header(self) -> str:
        return None

    @property
    def token(self):
        return None

    def sign_request(self, service, region, method, url, headers, payload, aws_access_key, aws_secret_key):
        # Generate timestamps
        amz_date = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        date_stamp = datetime.datetime.utcnow().strftime("%Y%m%d")

        # Canonical URI
        parsed_url = urlparse(url)
        canonical_uri = parsed_url.path or "/"

        # Prepare payload
        payload_str = json.dumps(payload)
        payload_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

        # Canonical headers (sorted by lowercase header name)
        sorted_headers = sorted(headers.items(), key=lambda x: x[0].lower())
        canonical_headers = "".join([f"{k.lower()}:{v.strip()}\n" for k, v in sorted_headers])
        signed_headers = ";".join(sorted(k.lower() for k in headers.keys()))

        # Canonical request
        canonical_request = f"{method}\n{canonical_uri}\n\n{canonical_headers}\n{signed_headers}\n{payload_hash}"

        # String to sign
        algorithm = "AWS4-HMAC-SHA256"
        credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
        string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"

        # Signing key generation
        k_secret = ("AWS4" + aws_secret_key).encode("utf-8")
        k_date = hmac.new(k_secret, date_stamp.encode("utf-8"), hashlib.sha256).digest()
        k_region = hmac.new(k_date, region.encode("utf-8"), hashlib.sha256).digest()
        k_service = hmac.new(k_region, service.encode("utf-8"), hashlib.sha256).digest()
        signing_key = hmac.new(k_service, b"aws4_request", hashlib.sha256).digest()

        # Signature
        signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

        # Authorization header
        authorization_header = (
            f"{algorithm} Credential={aws_access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
        )

        return authorization_header, amz_date
