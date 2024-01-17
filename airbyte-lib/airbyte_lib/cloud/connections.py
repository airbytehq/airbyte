"""This module defines classes and methods for working with Airbyte Cloud and OSS connections."""
from __future__ import annotations

from abc import ABC, abstractmethod
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable

from overrides import overrides
from pydantic import BaseModel, PrivateAttr

from airbyte_lib.cloud import _api_util


if TYPE_CHECKING:
    from airbyte.models import shared as api_models
    from attr import dataclass


def requires_state(func: Callable[..., Any]) -> Callable[..., Any]:
    """A decorator that ensures that the state is loaded before calling the function."""

    @wraps(func)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        if self._cached_state is None:
            self.refresh_state()

        return func(self, *args, **kwargs)

    return wrapper


class HostedAirbyteResource(ABC, BaseModel):
    """Base class for a resource hosted on Airbyte Cloud, OSS, or Enterprise."""

    workspace_id: str
    api_root: str = "https://api.airbyte.com/v1"
    web_root: str = "https://cloud.airbyte.com"
    bearer_token: str | None = None

    _cached_state: dataclass | None = None
    """The cached state of the resource."""

    @abstractmethod
    def refresh_state(self) -> dataclass:
        """Fetch the state from the Airbyte API."""
        raise NotImplementedError


class HostedConnection(HostedAirbyteResource):
    """A Cloud or OSS connection between a source and destination."""

    connection_id: str

    _cached_state: api_models.ConnectionResponse | None = None

    @overrides
    def refresh_state(self) -> None:
        """Fetch the connection state from the Airbyte API."""
        self._cached_state = _api_util.get_connection(
            workspace_id=self.workspace_id,
            connection_id=self.connection_id,
            bearer_token=self.bearer_token
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
                bearer_token=self.bearer_token,
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
                bearer_token=self.bearer_token,
            )

        return self._cached_source

    def run(self) -> None:
        """Run the connection."""
        _api_util.run_connection(
            workspace_id=self.workspace_id,
            connection_id=self.connection_id,
            bearer_token=self.bearer_token,
        )


class HostedSource(HostedAirbyteResource):

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
        self._cached_state = _api_util.get_source(
            source_id=self.source_id,
            bearer_token=self.bearer_token
        )

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


class HostedDestination(HostedAirbyteResource):

    _cached_state: PrivateAttr(api_models.DestinationResponse) | None = None

    @overrides
    def refresh_state(self) -> None:
        """Fetch the connection state from the Airbyte API."""
        self._cached_state = _api_util.get_destination(
            destination_id=self.source_id,
            bearer_token=self.bearer_token,
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
