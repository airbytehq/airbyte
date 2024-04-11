#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import jwt
from datetime import datetime
from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Union, Optional

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.interpolation.interpolated_mapping import InterpolatedMapping

@dataclass
class JwtAuthenticator(DeclarativeAuthenticator):

    config: Mapping[str, Any]
    parameters: InitVar[Mapping[str, Any]]
    secret_key: Union[InterpolatedString, str]
    algorithm: Union[InterpolatedString, str]
    token_duration: Union[InterpolatedString, str] = None
    kid: Union[InterpolatedString, str] = None
    typ: Union[InterpolatedString, str] = "JWT"
    iss: Union[InterpolatedString, str] = None
    sub: Union[InterpolatedString, str] = None
    aud: Union[InterpolatedString, str] = None
    cty: Union[InterpolatedString, str] = None
    additional_jwt_headers: Mapping[str, Any] = None
    additional_jwt_payload: Mapping[str, Any] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__init__()
        self._algorithm = InterpolatedString.create(self.algorithm, parameters=parameters)
        self._secret_key = InterpolatedString.create(self.secret_key, parameters=parameters)
        self._kid = InterpolatedString.create(self.kid, parameters=parameters)
        self._typ = InterpolatedString.create(self.typ, parameters=parameters)
        self._iss = InterpolatedString.create(self.iss, parameters=parameters)
        self._sub = InterpolatedString.create(self.sub, parameters=parameters)
        self._aud = InterpolatedString.create(self.aud, parameters=parameters)
        self._cty = InterpolatedString.create(self.cty, parameters=parameters)
        self._token_duration = InterpolatedString.create(self.token_duration, parameters=parameters)
        self._additional_jwt_headers = InterpolatedMapping(self.additional_jwt_headers or {}, parameters=parameters)
        self._additional_jwt_payload = InterpolatedMapping(self.additional_jwt_headers or {}, parameters=parameters)

    def _get_algorithm(self) -> str:
        algorithm: str = self._algorithm.eval(self.config)
        if not algorithm:
            raise ValueError("Algorithm is required")
        return algorithm

    def _get_secret_key(self) -> str:
        secret_key: str = self._secret_key.eval(self.config)
        if not secret_key:
            raise ValueError("secret_key is required")
        return secret_key

    def _get_jwt_headers(self) -> Mapping[str, Any]:
        headers = {}
        headers.update(self._additional_jwt_headers.eval(self.config))
        if self._kid:
            headers["kid"] = f"{self._kid.eval(self.config)}"
        if self._algorithm:
            headers["alg"] = self._get_algorithm()
        if self._typ:
            headers["typ"] = self._typ
        if self._cty:
            headers["cty"] = self._cty
        return headers

    def _get_jwt_payload(self) -> Mapping[str, Any]:
        now = int(datetime.now().timestamp())
        payload = {}
        if self._token_duration:
            exp = now + int(self._token_duration.eval(self.config))
            payload["exp"] = exp
        nbf = now
        payload.update(self._additional_jwt_payload.eval(self.config))
        if self._iss:
            payload["iss"] = f"{self._iss.eval(self.config)}"
        if self._sub:
            payload["sub"] = self._sub
        if self._aud:
            payload["aud"] = self._aud
        payload["iat"] = now
        payload["nbf"] = nbf
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
