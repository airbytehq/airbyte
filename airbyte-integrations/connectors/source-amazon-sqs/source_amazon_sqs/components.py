#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import datetime
import hashlib
import hmac
from dataclasses import dataclass
from typing import Any, Mapping, Union
from urllib.parse import urlencode

import requests
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator, NoAuth
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

    def __post_init__(self, parameters: Mapping[str, Any]):
        self._access_key = InterpolatedString.create(self.access_key, parameters=parameters).eval(self.config)
        self._secret_key = InterpolatedString.create(self.secret_key, parameters=parameters).eval(self.config)
        self._region = InterpolatedString.create(self.region, parameters=parameters).eval(self.config)
        self._attributes_to_return = InterpolatedString.create(self.attributes_to_return, parameters=parameters).eval(self.config)
        self._queue_url = InterpolatedString.create(self.queue_url, parameters=parameters).eval(self.config)
        self._visibility_timeout = InterpolatedString.create(self.visibility_timeout, parameters=parameters).eval(self.config)
        self._max_wait_time = InterpolatedString.create(self.max_wait_time, parameters=parameters).eval(self.config)
        self.service = "sqs"

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        """Attach the HTTP headers and sign the SQS request."""
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Host": f"sqs.{self._region}.amazonaws.com",
        }

        # Parse the query string from the URL
        query_string = request.body.decode("utf-8") if request.body else ""
        query_params = {}
        if query_string:
            try:
                query_params = {item.split("=")[0]: item.split("=")[1] for item in query_string.split("&") if "=" in item}
            except Exception as e:
                # Log the error or handle it appropriately
                print(f"Error parsing query string: {e}")

        new_params = {
            "Action": "ReceiveMessage",
            "MessageAttributeNames": self._attributes_to_return.split(",") if self._attributes_to_return else [],
            "QueueUrl": self._queue_url,
            "VisibilityTimeout": self._visibility_timeout,
            "WaitTimeSeconds": self._max_wait_time,
        }

        # Update query_params with new_params, overwriting where necessary
        query_params.update(new_params)

        # Sign the AWS request
        authorization_header, amz_date = self.sign_aws_request(
            self.service,
            self._region,
            request.method,
            request.url,
            self.headers,
            query_params,
            self._access_key,
            self._secret_key,
        )
        self.headers["X-Amz-Date"] = amz_date
        self.headers["Authorization"] = authorization_header
        request.headers.update(self.headers)
        return request

    @property
    def auth_header(self) -> str:
        return None

    @property
    def token(self):
        return None

    def sign_aws_request(self, service, region, method, url, headers, query_params, aws_access_key, aws_secret_key):
        # Generate timestamps
        amz_date = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        date_stamp = datetime.datetime.utcnow().strftime("%Y%m%d")

        # Create canonical request
        canonical_uri = "/"
        canonical_querystring = "&".join(f"{key}={value}" for key, value in sorted(query_params.items()))
        canonical_headers = "".join([f"{key.lower()}:{value.strip()}\n" for key, value in sorted(headers.items())])
        signed_headers = ";".join(sorted(key.lower() for key in headers))
        payload_hash = hashlib.sha256("".encode()).hexdigest()  # SQS uses an empty payload
        canonical_request = f"{method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"

        # String to sign
        algorithm = "AWS4-HMAC-SHA256"
        credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
        string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n" + hashlib.sha256(canonical_request.encode()).hexdigest()

        # Generate signing key
        secret = ("AWS4" + aws_secret_key).encode()
        k_date = hmac.new(secret, date_stamp.encode(), hashlib.sha256).digest()
        k_region = hmac.new(k_date, region.encode(), hashlib.sha256).digest()
        k_service = hmac.new(k_region, service.encode(), hashlib.sha256).digest()
        k_signing = hmac.new(k_service, b"aws4_request", hashlib.sha256).digest()

        # Generate signature
        signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()

        # Authorization header
        authorization_header = (
            f"{algorithm} Credential={aws_access_key}/{credential_scope}, " f"SignedHeaders={signed_headers}, Signature={signature}"
        )
        return authorization_header, amz_date
