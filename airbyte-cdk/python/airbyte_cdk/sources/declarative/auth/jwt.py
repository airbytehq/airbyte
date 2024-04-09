#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import jwt
from datetime import datetime
from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Union

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString

@dataclass
class JwtAuthenticator(DeclarativeAuthenticator):

    config: Mapping[str, Any]
    parameters: InitVar[Mapping[str, Any]]
    secret_key: Union[InterpolatedString, str]
    algorithm: Union[InterpolatedString, str] = "ES256"
    kid: Union[InterpolatedString, str] = None
    typ: Union[InterpolatedString, str] = "JWT"
    iss: Union[InterpolatedString, str] = None
    sub: Union[InterpolatedString, str] = None
    aud: Union[InterpolatedString, str] = None
    iat: Union[InterpolatedString, str] = str(int(datetime.now().timestamp()))
    exp: Union[InterpolatedString, str] = str(int(datetime.now().timestamp()) + 1200)
    nbf: Union[InterpolatedString, str] = None
    jti: Union[InterpolatedString, str] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__init__()
        self._algorithm = InterpolatedString.create(self.algorithm, parameters=parameters)
        self._secret_key = InterpolatedString.create(self.secret_key, parameters=parameters)
        self._kid = InterpolatedString.create(self.kid, parameters=parameters)
        self._typ = InterpolatedString.create(self.typ, parameters=parameters)
        self._iss = InterpolatedString.create(self.iss, parameters=parameters)
        self._sub = InterpolatedString.create(self.sub, parameters=parameters)
        self._aud = InterpolatedString.create(self.aud, parameters=parameters)
        self._iat = InterpolatedString.create(self.iat, parameters=parameters)
        self._exp = InterpolatedString.create(self.exp, parameters=parameters)
        self._nbf = InterpolatedString.create(self.nbf, parameters=parameters)
        self._jti = InterpolatedString.create(self.jti, parameters=parameters)

    def _get_algorithm(self) -> str:
        # return self._algorithm
        return "ES256"

    def _get_jwt_headers(self) -> Mapping[str, Any]:
        return {
            "kid": "H65WG9K573",
            "alg": "ES256",
            "typ": "JWT"
        }

    def _get_jwt_payload(self) -> Mapping[str, Any]:
        now = int(datetime.now().timestamp())
        exp = now + 1200
        payload = {}
        if self._iss:
            payload["iss"] = "5e47079b-d162-4211-a21b-790fd74674cc"
        if self._sub:
            payload["sub"] = str(self._sub)
        if self._aud:
            payload["aud"] = "appstoreconnect-v1"
        if self._iat:
            payload["iat"] = str(self._iat)
        if self._exp:
            payload["exp"] = str(self._exp)
        if self._nbf:
            payload["nbf"] = str(self._nbf)
        if self._jti:
            payload["jti"] = str(self._jti)
        return {
            "iss": "5e47079b-d162-4211-a21b-790fd74674cc",
            "aud": "appstoreconnect-v1",
            "iat": now,
            "exp": exp,
        }

    def _get_secret_key(self) -> str:
        return "-----BEGIN PRIVATE KEY-----\nMIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQgVpC5M3YzVOusVW5c\n5G8KuORJkrauiS4ipfzskWrgxiygCgYIKoZIzj0DAQehRANCAASpA9ygPhQR3a/K\nLFPgPbFrY3VPM8RHCQGc1PMiOYm/Ebr/60MsYjAVXPOZGIpG4xbvIRdRycSLpzEO\nyPnkI1rh\n-----END PRIVATE KEY-----\n"

    def _get_signed_token(self) -> str:
        return jwt.encode(
            payload=self._get_jwt_payload(),
            key=self._get_secret_key(),
            algorithm=self._get_algorithm(),
            headers=self._get_jwt_headers(),
        )

    @property
    def auth_header(self) -> str:
        return "Authorization"

    @property
    def token(self) -> str:
        return f"Bearer {self._get_signed_token()}"