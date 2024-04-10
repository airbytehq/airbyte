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
        return f"{self._algorithm.eval(self.config)}"

    def _get_jwt_headers(self) -> Mapping[str, Any]:
        headers = {}
        if self._kid:
            headers["kid"] = f"{self._kid.eval(self.config)}"
        if self._algorithm:
            headers["alg"] = self._get_algorithm()
        if self._typ:
            headers["typ"] = f"{self._typ.eval(self.config)}"
        return headers

    def _get_jwt_payload(self) -> Mapping[str, Any]:
        now = int(datetime.now().timestamp())
        exp = now + 1200
        payload = {}
        if self._iss:
            payload["iss"] = f"{self._iss.eval(self.config)}"
        if self._sub:
            payload["sub"] = f"{self._sub.eval(self.config)}"
        if self._aud:
            payload["aud"] = f"{self._aud.eval(self.config)}"
        if self._iat:
            payload["iat"] = now
        if self._exp:
            payload["exp"] = exp
        if self._nbf:
            payload["nbf"] = self._nbf.eval(self.config)
        if self._jti:
            payload["jti"] = f"{self._jti.eval(self.config)}"
        return payload

    def _get_secret_key(self) -> str:
        return f"{self._secret_key.eval(self.config)}"

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
