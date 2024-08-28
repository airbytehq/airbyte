# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Optional

from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_oauth import AbstractOauth2Authenticator


@dataclass
class SignedAuthenticator(AbstractOauth2Authenticator):
    pass
