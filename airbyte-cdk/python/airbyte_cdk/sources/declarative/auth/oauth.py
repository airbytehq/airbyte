#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass, field
from typing import Any, List, Mapping, Optional, Union

import pendulum
from airbyte_cdk.sources.declarative.interpolation.interpolated_mapping import InterpolatedMapping
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_oauth import AbstractOauth2Authenticator
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class DeclarativeOauth2Authenticator(AbstractOauth2Authenticator, JsonSchemaMixin):
    """
    Generates OAuth2.0 access tokens from an OAuth2.0 refresh token and client credentials based on
    a declarative connector configuration file. Credentials can be defined explicitly or via interpolation
    at runtime. The generated access token is attached to each request via the Authorization header.

    Attributes:
        token_refresh_endpoint (Union[InterpolatedString, str]): The endpoint to refresh the access token
        client_id (Union[InterpolatedString, str]): The client id
        client_secret (Union[InterpolatedString, str]): Client secret
        refresh_token (Union[InterpolatedString, str]): The token used to refresh the access token
        config (Mapping[str, Any]): The user-provided configuration as specified by the source's spec
        scopes (Optional[List[str]]): The scopes to request
        token_expiry_date (Optional[Union[InterpolatedString, str]]): The access token expiration date
        access_token_name (Union[InterpolatedString, str]): THe field to extract access token from in the response
        expires_in_name (Union[InterpolatedString, str]): The field to extract expires_in from in the response
        refresh_request_body (Optional[Mapping[str, Any]]): The request body to send in the refresh request
    """

    token_refresh_endpoint: Union[InterpolatedString, str]
    client_id: Union[InterpolatedString, str]
    client_secret: Union[InterpolatedString, str]
    refresh_token: Union[InterpolatedString, str]
    access_token_name: Union[InterpolatedString, str]
    expires_in_name: Union[InterpolatedString, str]
    config: Mapping[str, Any] = field(default_factory=dict)
    refresh_request_body: Optional[Mapping[str, Any]] = (None,)
    scopes: Optional[List[str]] = None
    refresh_token_expiry_date: Optional[Union[InterpolatedString, str]] = None  # this is a hack and point it out in the review
    _token_expiry_date: pendulum.DateTime = field(init=False, repr=False)

    def __post_init__(self, options: Mapping[str, Any]):
        self.token_refresh_endpoint = InterpolatedString.create(self.token_refresh_endpoint)
        self.client_secret = InterpolatedString.create(self.client_secret)
        self.client_id = InterpolatedString.create(self.client_id)
        self.refresh_token = InterpolatedString.create(self.refresh_token)
        self.access_token_name = InterpolatedString.create(self.access_token_name or "access_token")
        self.expires_in_name = InterpolatedString.create(self.expires_in_name or "expires_in")
        self._refresh_request_body = InterpolatedMapping(self.refresh_request_body or {})

        self.token_expiry_date = (
            pendulum.parse(InterpolatedString.create(self.refresh_token_expiry_date).eval(self.config))
            if self.refresh_token_expiry_date
            else pendulum.now().subtract(days=1)
        )
        self.access_token = None

    def __init__(
        self,
        token_refresh_endpoint: Union[InterpolatedString, str],
        client_id: Union[InterpolatedString, str],
        client_secret: Union[InterpolatedString, str],
        refresh_token: Union[InterpolatedString, str],
        config: Mapping[str, Any],
        scopes: Optional[List[str]] = None,
        token_expiry_date: Optional[Union[InterpolatedString, str]] = None,
        access_token_name: Union[InterpolatedString, str] = "access_token",
        expires_in_name: Union[InterpolatedString, str] = "expires_in",
        refresh_request_body: Optional[Mapping[str, Any]] = None,
        **options: Optional[Mapping[str, Any]],
    ):
        """
        :param token_refresh_endpoint: The endpoint to refresh the access token
        :param client_id: The client id
        :param client_secret: Client secret
        :param refresh_token: The token used to refresh the access token
        :param config: The user-provided configuration as specified by the source's spec
        :param scopes: The scopes to request
        :param token_expiry_date: The access token expiration date
        :param access_token_name: THe field to extract access token from in the response
        :param expires_in_name:The field to extract expires_in from in the response
        :param refresh_request_body: The request body to send in the refresh request
        :param options: Additional runtime parameters to be used for string interpolation
        """
        self.config = config
        self.token_refresh_endpoint = InterpolatedString.create(token_refresh_endpoint, options=options)
        self.client_secret = InterpolatedString.create(client_secret, options=options)
        self.client_id = InterpolatedString.create(client_id, options=options)
        self.refresh_token = InterpolatedString.create(refresh_token, options=options)
        self.scopes = scopes
        self.access_token_name = InterpolatedString.create(access_token_name, options=options)
        self.expires_in_name = InterpolatedString.create(expires_in_name, options=options)
        self.refresh_request_body = InterpolatedMapping(refresh_request_body or {}, options=options)

        self.token_expiry_date = (
            pendulum.parse(InterpolatedString.create(token_expiry_date, options=options).eval(self.config))
            if token_expiry_date
            else pendulum.now().subtract(days=1)
        )
        self.access_token = None

    # def config(self) -> Mapping[str, Any]:
    #     return self.config
    #
    # def config(self, value: Mapping[str, Any]):
    #     self.config = value

    def token_refresh_endpoint(self) -> str:
        return self.token_refresh_endpoint.eval(self.config)

    @property
    def client_id(self) -> str:
        return self.client_id.eval(self.config)

    def client_secret(self) -> str:
        return self.client_secret.eval(self.config)

    def refresh_token(self) -> str:
        return self.refresh_token.eval(self.config)

    def scopes(self) -> [str]:
        return self.scopes

    # @scopes.setter
    # def scopes(self, value: [str]):
    #     self._scopes = value

    @property
    def token_expiry_date(self) -> pendulum.DateTime:
        # This is so complicated
        return self._token_expiry_date

    @token_expiry_date.setter
    def token_expiry_date(self, value: pendulum.DateTime):
        # I dunno fuck mane, can we jus skip this on the onset...
        self._token_expiry_date = value

    def access_token_name(self) -> InterpolatedString:
        return self.access_token_name.eval(self.config)

    # @access_token_name.setter
    # def access_token_name(self, value: InterpolatedString):
    #     self._access_token_name = value

    def expires_in_name(self) -> InterpolatedString:
        return self.expires_in_name.eval(self.config)

    # @expires_in_name.setter
    # def expires_in_name(self, value: InterpolatedString):
    #     self._expires_in_name = value

    def refresh_request_body(self) -> Mapping[str, Any]:
        return self._refresh_request_body.eval(self.config)

    # @refresh_request_body.setter
    # def refresh_request_body(self, value: InterpolatedMapping):
    #     self._refresh_request_body = value

    @property
    def access_token(self) -> str:
        return self._access_token

    @access_token.setter
    def access_token(self, value: str):
        self._access_token = value
