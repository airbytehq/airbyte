#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
from dataclasses import InitVar, dataclass
from datetime import datetime
from typing import Any, Mapping, Optional, Union

import jwt
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.interpolation.interpolated_mapping import InterpolatedMapping
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString


class JwtAlgorithm(str):
    """
    Enum for supported JWT algorithms
    """

    HS256 = "HS256"
    HS384 = "HS384"
    HS512 = "HS512"
    ES256 = "ES256"
    ES256K = "ES256K"
    ES384 = "ES384"
    ES512 = "ES512"
    RS256 = "RS256"
    RS384 = "RS384"
    RS512 = "RS512"
    PS256 = "PS256"
    PS384 = "PS384"
    PS512 = "PS512"
    EdDSA = "EdDSA"


@dataclass
class JwtAuthenticator(DeclarativeAuthenticator):
    """
    Generates a JSON Web Token (JWT) based on a declarative connector configuration file. The generated token is attached to each request via the Authorization header.

    Attributes:
        config (Mapping[str, Any]): The user-provided configuration as specified by the source's spec
        secret_key (Union[InterpolatedString, str]): The secret key used to sign the JWT
        algorithm (Union[str, JwtAlgorithm]): The algorithm used to sign the JWT
        token_duration (Optional[int]): The duration in seconds for which the token is valid
        base64_encode_secret_key (Optional[Union[InterpolatedBoolean, str, bool]]): Whether to base64 encode the secret key
        header_prefix (Optional[Union[InterpolatedString, str]]): The prefix to add to the Authorization header
        kid (Optional[Union[InterpolatedString, str]]): The key identifier to be included in the JWT header
        typ (Optional[Union[InterpolatedString, str]]): The type of the JWT.
        cty (Optional[Union[InterpolatedString, str]]): The content type of the JWT.
        iss (Optional[Union[InterpolatedString, str]]): The issuer of the JWT.
        sub (Optional[Union[InterpolatedString, str]]): The subject of the JWT.
        aud (Optional[Union[InterpolatedString, str]]): The audience of the JWT.
        additional_jwt_headers (Optional[Mapping[str, Any]]): Additional headers to include in the JWT.
        additional_jwt_payload (Optional[Mapping[str, Any]]): Additional payload to include in the JWT.
    """

    config: Mapping[str, Any]
    parameters: InitVar[Mapping[str, Any]]
    secret_key: Union[InterpolatedString, str]
    algorithm: Union[str, JwtAlgorithm]
    token_duration: Optional[int]
    base64_encode_secret_key: Optional[Union[InterpolatedBoolean, str, bool]] = False
    header_prefix: Optional[Union[InterpolatedString, str]] = None
    kid: Optional[Union[InterpolatedString, str]] = None
    typ: Optional[Union[InterpolatedString, str]] = None
    cty: Optional[Union[InterpolatedString, str]] = None
    iss: Optional[Union[InterpolatedString, str]] = None
    sub: Optional[Union[InterpolatedString, str]] = None
    aud: Optional[Union[InterpolatedString, str]] = None
    additional_jwt_headers: Optional[Mapping[str, Any]] = None
    additional_jwt_payload: Optional[Mapping[str, Any]] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._secret_key = InterpolatedString.create(self.secret_key, parameters=parameters)
        self._algorithm = JwtAlgorithm(self.algorithm) if isinstance(self.algorithm, str) else self.algorithm
        self._base64_encode_secret_key = (
            InterpolatedBoolean(self.base64_encode_secret_key, parameters=parameters)
            if isinstance(self.base64_encode_secret_key, str)
            else self.base64_encode_secret_key
        )
        self._token_duration = self.token_duration
        self._header_prefix = InterpolatedString.create(self.header_prefix, parameters=parameters) if self.header_prefix else None
        self._kid = InterpolatedString.create(self.kid, parameters=parameters) if self.kid else None
        self._typ = InterpolatedString.create(self.typ, parameters=parameters) if self.typ else None
        self._cty = InterpolatedString.create(self.cty, parameters=parameters) if self.cty else None
        self._iss = InterpolatedString.create(self.iss, parameters=parameters) if self.iss else None
        self._sub = InterpolatedString.create(self.sub, parameters=parameters) if self.sub else None
        self._aud = InterpolatedString.create(self.aud, parameters=parameters) if self.aud else None
        self._additional_jwt_headers = InterpolatedMapping(self.additional_jwt_headers or {}, parameters=parameters)
        self._additional_jwt_payload = InterpolatedMapping(self.additional_jwt_payload or {}, parameters=parameters)

    def _get_jwt_headers(self) -> dict[str, Any]:
        """ "
        Builds and returns the headers used when signing the JWT.
        """
        headers = self._additional_jwt_headers.eval(self.config)
        if any(prop in headers for prop in ["kid", "alg", "typ", "cty"]):
            raise ValueError("'kid', 'alg', 'typ', 'cty' are reserved headers and should not be set as part of 'additional_jwt_headers'")

        if self._kid:
            headers["kid"] = self._kid.eval(self.config)
        if self._typ:
            headers["typ"] = self._typ.eval(self.config)
        if self._cty:
            headers["cty"] = self._cty.eval(self.config)
        headers["alg"] = self._algorithm
        return headers

    def _get_jwt_payload(self) -> dict[str, Any]:
        """
        Builds and returns the payload used when signing the JWT.
        """
        now = int(datetime.now().timestamp())
        exp = now + self._token_duration if isinstance(self._token_duration, int) else now
        nbf = now

        payload = self._additional_jwt_payload.eval(self.config)
        if any(prop in payload for prop in ["iss", "sub", "aud", "iat", "exp", "nbf"]):
            raise ValueError(
                "'iss', 'sub', 'aud', 'iat', 'exp', 'nbf' are reserved properties and should not be set as part of 'additional_jwt_payload'"
            )

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
        """
        Returns the secret key used to sign the JWT.
        """
        secret_key: str = self._secret_key.eval(self.config)
        return base64.b64encode(secret_key.encode()).decode() if self._base64_encode_secret_key else secret_key

    def _get_signed_token(self) -> Union[str, Any]:
        """
        Signed the JWT using the provided secret key and algorithm and the generated headers and payload. For additional information on PyJWT see: https://pyjwt.readthedocs.io/en/stable/
        """
        try:
            return jwt.encode(
                payload=self._get_jwt_payload(),
                key=self._get_secret_key(),
                algorithm=self._algorithm,
                headers=self._get_jwt_headers(),
            )
        except Exception as e:
            raise ValueError(f"Failed to sign token: {e}")

    def _get_header_prefix(self) -> Union[str, None]:
        """
        Returns the header prefix to be used when attaching the token to the request.
        """
        return self._header_prefix.eval(self.config) if self._header_prefix else None

    @property
    def auth_header(self) -> str:
        return "Authorization"

    @property
    def token(self) -> str:
        return f"{self._get_header_prefix()} {self._get_signed_token()}" if self._get_header_prefix() else self._get_signed_token()
