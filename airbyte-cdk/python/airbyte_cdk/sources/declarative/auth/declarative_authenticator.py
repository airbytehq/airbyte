#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Callable, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.models.declarative_component_schema import NoAuth as NoAuthModel
from airbyte_cdk.sources.declarative.parsers.component_constructor import ComponentConstructor
from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_token import AbstractHeaderAuthenticator
from airbyte_cdk.sources.types import Config


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
class NoAuth(DeclarativeAuthenticator, ComponentConstructor[NoAuthModel, NoAuthModel]):
    parameters: InitVar[Mapping[str, Any]]

    @classmethod
    def resolve_dependencies(
        cls,
        model: NoAuthModel,
        config: Config,
        dependency_constructor: Callable[[NoAuthModel, Config], Any],
        additional_flags: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> Mapping[str, Any]:
        print(f"Model: {model}, type: {type(model)}")
        return {"parameters": model.parameters or {}}

    @property
    def auth_header(self) -> str:
        return ""

    @property
    def token(self) -> str:
        return ""
