"""This module defines classes and methods for working with Airbyte Cloud and OSS connections."""
from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, Any, Callable

from overrides import overrides

from airbyte_lib.cloud import _api_util
from airbyte_lib.cloud._remote_sync import SyncMode, sync_source_definition
from airbyte_lib.cloud.resources import HostedAirbyteResource


if TYPE_CHECKING:
    from airbyte.models import shared as api_models
    from attr import dataclass
    from pydantic import PrivateAttr

    from airbyte_lib.cloud.hosts import HostedAirbyteInstance
    from airbyte_lib.source import Source


def requires_state(func: Callable[..., Any]) -> Callable[..., Any]:
    """A decorator that ensures that the state is loaded before calling the function."""

    @wraps(func)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        if self._cached_state is None:
            self.refresh_state()

        return func(self, *args, **kwargs)

    return wrapper


class HostedConnection(HostedAirbyteResource):
    """A Cloud or OSS connection between a source and destination."""

    connection_id: str

    _cached_state: api_models.ConnectionResponse | None = None

    @overrides
    def refresh_state(self) -> None:
        """Fetch the connection state from the Airbyte API."""
        self._cached_state = _api_util.get_connection(
            workspace_id=self.workspace_id, connection_id=self.connection_id, api_key=self.api_key
        )

    @property
    def workspace_url(self) -> str:
        """Get the workspace URL."""
        return f"https://cloud.airbyte.io/workspace/{self.workspace_id}"

    @property
    def destination(self) -> HostedDestination:
        """Get the destination URL.

        If connection state has not yet been loaded, we will attempt to load it.
        """
        if self._cached_source is None:
            self._cached_source = HostedDestination(
                workspace_id=self.workspace_id,
                destination_id=self._state.destination_id,
                api_key=self.api_key,
            )

        return self._cached_destination

    @property
    def source(self) -> HostedDestination:
        """Get the destination URL.

        If connection state has not yet been loaded, we will attempt to load it.
        """
        if self._cached_source is None:
            self._cached_source = HostedSource(
                workspace_id=self.workspace_id,
                source_id=self._state.source_id,
                api_key=self.api_key,
            )

        return self._cached_source

    def run(self) -> None:
        """Run the connection."""
        _api_util.run_connection(
            workspace_id=self.workspace_id,
            connection_id=self.connection_id,
            api_key=self.api_key,
        )


class HostedSource(HostedAirbyteResource):
    """A Cloud, OSS, or Enterprise-hosted source."""

    _cached_state: api_models.SourceResponse | None = None

    @overrides
    @property
    def _state(self) -> api_models.SourceResponse:
        if self._cached_state is None:
            self.refresh_state()

        return self._cached_state

    @overrides
    def refresh_state(self) -> None:
        """Fetch the connection state from the Airbyte API."""
        self._cached_state = _api_util.get_source(source_id=self.source_id, api_key=self.api_key)

    @requires_state
    def get_config(self) -> dataclass:
        """Get the destination config."""
        return self._state.configuration

    @requires_state
    @property
    def source_type(self) -> str:
        """Get the source type."""
        return self._state.source_type

    @requires_state
    @property
    def name(self) -> str:
        """Get the source type."""
        return self._state.name

    @classmethod
    def from_local_source(
        cls,
        source: Source,
        name: str,
        airbyte_instance: HostedAirbyteInstance,
        sync_mode: SyncMode = SyncMode.FAIL,
    ) -> HostedSource:
        """Create a hosted source from a local source.

        The 'name' arg is required and will be used for deduping, according to the provided
        sync_mode.
        """
        sync_source_definition(
            source=source,
            airbyte_instance=airbyte_instance,
            name=name,
            on_duplicate=sync_mode,
        )


class HostedDestination(HostedAirbyteResource):
    _cached_state: PrivateAttr(api_models.DestinationResponse) | None = None

    @overrides
    def refresh_state(self) -> None:
        """Fetch the connection state from the Airbyte API."""
        self._cached_state = _api_util.get_destination(
            destination_id=self.source_id,
            api_key=self.api_key,
        )

    @requires_state
    def get_config(self) -> dataclass:
        """Get the destination config."""
        return self._state.configuration

    @requires_state
    @property
    def destination_type(self) -> str:
        """Get the source type."""
        return self._state.destination_type

    @requires_state
    @property
    def name(self) -> str:
        """Get the source type."""
        return self._state.name
