#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, List, Mapping

import dpath
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator


@dataclass
class SelectiveAuthenticator(DeclarativeAuthenticator):
    """Authenticator that selects concrete implementation based on specific config value."""

    config: Mapping[str, Any]
    authenticators: List[str, DeclarativeAuthenticator]
    authenticator_selection_path: List[str]

    def __new__(
        cls,
        config: Mapping[str, Any],
        authenticators: Mapping[str, DeclarativeAuthenticator],
        authenticator_selection_path: List[str],
        *args,
        **kwargs,
    ):
        try:
            selected_key = str(dpath.util.get(config, authenticator_selection_path))
        except KeyError as err:
            raise ValueError("The path from `authenticator_selection_path` is not found in the config.") from err

        try:
            return authenticators[selected_key]
        except KeyError as err:
            raise ValueError(f"The authenticator `{selected_key}` is not found.") from err
