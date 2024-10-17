# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""State backend implementation."""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING

from airbyte_cdk.models import AirbyteStreamState


if TYPE_CHECKING:
    from airbyte_cdk.models import (
        AirbyteStreamState,
    )

    from airbyte_cdk.sql.state_providers import StateProviderBase
    from airbyte_cdk.sql.state_writers import StateWriterBase


class StateBackendBase(abc.ABC):
    """A class which manages the stream state for data synced.

    The backend is responsible for storing and retrieving the state of streams. It generates
    `StateProvider` objects, which are paired to a specific source and table prefix.
    """

    def __init__(self) -> None:
        """Initialize the state manager with a static catalog state."""
        self._state_artifacts: list[AirbyteStreamState] | None = None

    @abc.abstractmethod
    def get_state_provider(
        self,
        source_name: str,
        table_prefix: str,
        *,
        refresh: bool = True,
        destination_name: str | None = None,
    ) -> StateProviderBase:
        """Return the state provider."""
        ...

    @abc.abstractmethod
    def get_state_writer(
        self,
        source_name: str,
        destination_name: str | None = None,
    ) -> StateWriterBase:
        """Return a state writer for a named source.

        The same table prefix of the backend will be used for the state writer.
        """
        ...

    def _initialize_backend(
        self,
        *,
        force_refresh: bool = False,
    ) -> None:
        """Do any needed initialization, for instance to load state artifacts from the cache.

        By default, this method does nothing. Base classes may override this method to load state
        artifacts or perform other initialization tasks.
        """
        _ = force_refresh  # Unused
        pass
