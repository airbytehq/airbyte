# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""State writer implementation."""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from airbyte_protocol.models.airbyte_protocol import AirbyteStateMessage


class StateWriterBase(abc.ABC):
    """A class to write state artifacts."""

    @abc.abstractmethod
    def write_state(
        self,
        state_message: AirbyteStateMessage,
    ) -> None:
        """Save or 'write' a state artifact."""
        ...


class StdOutStateWriter(StateWriterBase):
    """A state writer that writes state artifacts to stdout.

    This is required when we are functioning as a "Destination" in the Airbyte protocol, and
    an orchestrator is responsible for saving those state artifacts.
    """

    def write_state(
        self,
        state_message: AirbyteStateMessage,
    ) -> None:
        """Save or 'write' a state artifact."""
        print(state_message.json())
