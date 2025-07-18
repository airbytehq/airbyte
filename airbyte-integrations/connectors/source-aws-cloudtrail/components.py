#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import datetime
import hashlib
import hmac
import json
from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Union

import requests

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import NoAuth
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.types import Config


@dataclass
class CustomAuthenticator(NoAuth):
    config: Config
    aws_key_id: Union[InterpolatedString, str]
    aws_secret_key: Union[InterpolatedString, str]
    aws_region_name: Union[InterpolatedString, str]

    def __post_init__(self, parameters: Mapping[str, Any]):
        self._aws_key_id = InterpolatedString.create(self.aws_key_id, parameters=parameters).eval(self.config)
        self._aws_secret_key = InterpolatedString.create(self.aws_secret_key, parameters=parameters).eval(self.config)
        self._aws_region_name = InterpolatedString.create(self.aws_region_name, parameters=parameters).eval(self.config)
        self.path = "/"
        self.service = "cloudtrail"

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        """Attach the HTTP headers required to authenticate on the HTTP request"""
        self.headers = {
            "Content-Type": "application/x-amz-json-1.1",
            "Accept": "application/json",
            "Host": f"cloudtrail.{self._aws_region_name}.amazonaws.com",
        }
        # StartTime and EndTime should be Unix timestamps with integer type
        request_body_json = json.loads(request.body.decode("utf-8"))
        if self.config.get("lookup_attributes_filter"):
            lookup_attributes_filter = self.config.get("lookup_attributes_filter", {})
            attribute_key = lookup_attributes_filter.get("attribute_key", "")
            attribute_value = lookup_attributes_filter.get("attribute_value", "")

            request_body_json["LookupAttributes"] = [{"AttributeKey": attribute_key, "AttributeValue": attribute_value}]
        request_body_json["StartTime"] = int(float(request_body_json["StartTime"]))
        request_body_json["EndTime"] = int(float(request_body_json["EndTime"]))
        request.body = json.dumps(request_body_json).encode("utf-8")
        # Sign the AWS Request and update headers with timestamp
        authorization_header, amz_date = self.sign_aws_request(
            self.service,
            self._aws_region_name,
            request.method,
            self.path,
            self.headers,
            request_body_json,
            self._aws_key_id,
            self._aws_secret_key,
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

    # AWS Cloudtrail Requires custom sign process with request, Referred from botocore client - https://github.com/boto/botocore/issues/786
    def sign_aws_request(self, service, region, method, path, headers, payload, aws_access_key, aws_secret_key):
        # Define required parameters for signing
        service = service
        region = region
        method = method
        path = path
        headers = headers
        string_payload = json.dumps(payload)
        payload_hash = hashlib.sha256(string_payload.encode()).hexdigest()

        # Generate timestamp and date for the request
        amz_date = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        date_stamp = datetime.datetime.utcnow().strftime("%Y%m%d")

        # Generate canonical request
        canonical_headers = "".join([f"{key.lower()}:{value.strip()}\n" for key, value in sorted(headers.items())])
        signed_headers = ";".join(sorted(key.lower() for key in headers))
        canonical_request = f"{method}\n{path}\n\n{canonical_headers}\n{signed_headers}\n{payload_hash}"

        # Generate string to sign
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

        # Generate authorization header
        authorization_header = (
            f"{algorithm} Credential={aws_access_key}/{credential_scope}, " f"SignedHeaders={signed_headers}, Signature={signature}"
        )
        return authorization_header, amz_date
