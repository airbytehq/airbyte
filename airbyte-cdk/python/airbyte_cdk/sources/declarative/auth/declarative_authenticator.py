#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Mapping

from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_token import AbstractHeaderAuthenticator


@dataclass
class DeclarativeAuthenticator:
    """
    Interface used to associate which authenticators can be used as part of the declarative framework
    """


@dataclass
class NoAuth(AbstractHeaderAuthenticator, DeclarativeAuthenticator):
    parameters: InitVar[Mapping[str, Any]]

    @property
    def auth_header(self) -> str:
        return ""

    @property
    def token(self) -> str:
        return ""
