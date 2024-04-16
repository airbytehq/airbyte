#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
from dataclasses import InitVar, dataclass
from datetime import datetime
from typing import Any, Mapping, Union

import jwt
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.interpolation.interpolated_mapping import InterpolatedMapping
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean


@dataclass
class JwtAuthenticator(DeclarativeAuthenticator):

    config: Mapping[str, Any]
    parameters: InitVar[Mapping[str, Any]]
    secret_key: Union[InterpolatedString, str]
    algorithm: Union[InterpolatedString, str]
    base64_encode_secret_key: Union[InterpolatedBoolean, bool] = False
    token_duration: int = None
    header_prefix: Union[InterpolatedString, str] = None
    kid: Union[InterpolatedString, str] = None
    typ: Union[InterpolatedString, str] = None
    iss: Union[InterpolatedString, str] = None
    sub: Union[InterpolatedString, str] = None
    aud: Union[InterpolatedString, str] = None
    cty: Union[InterpolatedString, str] = None
    additional_jwt_headers: Mapping[str, Any] = None
    additional_jwt_payload: Mapping[str, Any] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__init__()
        self._secret_key = InterpolatedString.create(self.secret_key, parameters=parameters)
        self._algorithm = InterpolatedString.create(self.algorithm, parameters=parameters)
        self._base64_encode_secret_key = InterpolatedBoolean(self.base64_encode_secret_key, parameters=parameters)
        self._token_duration = self.token_duration
        self._header_prefix = InterpolatedString.create(self.header_prefix, parameters=parameters)
        self._kid = InterpolatedString.create(self.kid, parameters=parameters)
        self._typ = InterpolatedString.create(self.typ, parameters=parameters)
        self._iss = InterpolatedString.create(self.iss, parameters=parameters)
        self._sub = InterpolatedString.create(self.sub, parameters=parameters)
        self._aud = InterpolatedString.create(self.aud, parameters=parameters)
        self._cty = InterpolatedString.create(self.cty, parameters=parameters)
        self._additional_jwt_headers = InterpolatedMapping(self.additional_jwt_headers or {}, parameters=parameters)
        self._additional_jwt_payload = InterpolatedMapping(self.additional_jwt_payload or {}, parameters=parameters)

    def _get_jwt_headers(self) -> Mapping[str, Any]:
        headers = self._additional_jwt_headers.eval(self.config)
        if any(prop in headers for prop in ["kid", "alg", "typ", "cty"]):
            raise ValueError("'kid', 'alg', 'typ', 'cty' are reserved headers and should not be set as part of 'additional_jwt_headers'")

        if self._kid:
            headers["kid"] = self._kid.eval(self.config)
        if self._typ:
            headers["typ"] = self._typ.eval(self.config)
        if self._cty:
            headers["cty"] = self._cty.eval(self.config)
        headers["alg"] = self._algorithm.eval(self.config)
        return headers

    def _get_jwt_payload(self) -> Mapping[str, Any]:
        now = int(datetime.now().timestamp())
        exp = now + self._token_duration
        nbf = now

        payload = self._additional_jwt_payload.eval(self.config)
        if any(prop in payload for prop in ["iss", "sub", "aud", "iat", "exp", "nbf"]):
            raise ValueError("'iss', 'sub', 'aud', 'iat', 'exp', 'nbf' are reserved properties and should not be set as part of 'additional_jwt_payload'")

        if self._iss:
            payload["iss"] = self._iss.eval(self.config)
        if self._sub:
            payload["sub"] = self._sub.eval(self.config)
        if self._aud:
            payload["aud"] = self._aud.eval(self.config)
        payload["iat"] = now
        payload["exp"] = exp
        payload["nbf"] = nbf
        return payload

    def _get_secret_key(self) -> str:
        secret_key: str = self._secret_key.eval(self.config)
        return base64.b64encode(secret_key.encode()).decode() if self._base64_encode_secret_key.eval(self.config) else secret_key

    def _get_signed_token(self) -> str:
        try:
            return jwt.encode(
                payload=self._get_jwt_payload(),
                key=self._get_secret_key(),
                algorithm=self._algorithm.eval(self.config),
                headers=self._get_jwt_headers(),
            )
        except Exception as e:
            raise ValueError(f"Failed to sign token: {e}")

    def _get_header_prefix(self) -> str:
        return self._header_prefix.eval(self.config) if self._header_prefix else None

    @property
    def auth_header(self) -> str:
        return "Authorization"

    @property
    def token(self) -> str:
        return f"{self._get_header_prefix()} {self._get_signed_token()}" if self._get_header_prefix() else self._get_signed_token()
