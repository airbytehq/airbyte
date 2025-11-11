#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Union

from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_token import (
    AbstractHeaderAuthenticator,
)


@dataclass
class DeclarativeAuthenticator(AbstractHeaderAuthenticator):
    """
    Interface used to associate which authenticators can be used as part of the declarative framework
    """

    def get_request_params(self) -> Mapping[str, Any]:
        """HTTP request parameter to add to the requests"""
        return {}

    def get_request_body_data(self) -> Union[Mapping[str, Any], str]:
        """Form-encoded body data to set on the requests"""
        return {}

    def get_request_body_json(self) -> Mapping[str, Any]:
        """JSON-encoded body data to set on the requests"""
        return {}


@dataclass
class NoAuth(DeclarativeAuthenticator):
    parameters: InitVar[Mapping[str, Any]]

    @property
    def auth_header(self) -> str:
        return ""

    @property
    def token(self) -> str:
        return ""
