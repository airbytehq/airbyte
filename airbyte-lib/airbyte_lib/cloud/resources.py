"""Base class for a resource hosted on Airbyte Cloud, OSS, or Enterprise."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pydantic import BaseModel

from airbyte_lib.cloud.hosts import HostedAirbyteInstance


if TYPE_CHECKING:
    from dataclasses import dataclass


class HostedAirbyteResourceBase(ABC, BaseModel):
    """Base class for a resource hosted on Airbyte Cloud, OSS, or Enterprise."""

    api_root: str = "https://api.airbyte.com/v1"
    web_root: str = "https://cloud.airbyte.com"
    api_key: str | None = None

    _cached_state: dataclass | None = None
    """The cached state of the resource."""

    @abstractmethod
    def refresh_state(self) -> dataclass:
        """Fetch the state from the Airbyte API."""
        raise NotImplementedError

    @property
    def airbyte_instance(self) -> HostedAirbyteInstance:
        """Get the Airbyte instance."""
        return HostedAirbyteInstance(
            api_key=self.api_key,
            api_root=self.api_root,
            web_root=self.web_root,
        )


class HostedWorkspace(HostedAirbyteResourceBase):
    """A Cloud workspace."""

    workspace_id: str


class HostedAirbyteResource(HostedAirbyteResourceBase):
    workspace_id: str

    @property
    def workspace(self) -> HostedWorkspace:
        """Get the workspace."""
        return HostedWorkspace(
            workspace_id=self.workspace_id,
            api_key=self.api_key,
            api_root=self.api_root,
            web_root=self.web_root,
        )
