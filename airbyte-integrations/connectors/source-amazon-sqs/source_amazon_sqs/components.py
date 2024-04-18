#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
from typing import Any, Mapping
from airbyte_cdk.sources.declarative.types import Config
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator


@dataclass
class AmazonSQSAuthenticator(DeclarativeAuthenticator):
    config: Config

    def get_auth_header(self) -> Mapping[str, Any]:
        """The header to set on outgoing HTTP requests"""

        date_time_stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        date_stamp      = datetime.now(timezone.utc).strftime('%Y%m%d')

        access_key = self.config.get("access_key")
        secret_key = self.config.get("secret_key")
        region     = self.config.get("region")

        service     = 'sqs'
        service_url = "sqs.amazonaws.com"

        algorithm      = 'AWS4-HMAC-SHA256'
        signed_headers = 'host;x-amz-date'

        credential_scope  = f"{date_stamp}/{region}/{service}/aws4_request"
        canonical_headers = f"host:{service_url}\nx-amz-date:{date_time_stamp}\n"
        payload_hash      = hashlib.sha256(('').encode('utf-8')).hexdigest()
        canonical_request = f"GET\n/\n\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
        string_to_sign = f"{algorithm}\n{date_time_stamp}\n{credential_scope}\n'{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"

        signing_key = self.get_signature_key(secret_key, date_stamp, region, service)
        signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()

        authorization_header = f"{algorithm} Credential={access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"

        return {'x-amz-date':date_time_stamp, 'Authorization':authorization_header}

    def get_signature_key(self, key, date_stamp, region_name, service_name):
        k_date = self.sign((f"AWS4{key}").encode('utf-8'), date_stamp)
        k_region = self.sign(k_date, region_name)
        k_service = self.sign(k_region, service_name)
        k_signing = self.sign(k_service, 'aws4_request')
        return k_signing  
    
    def sign(self, key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
