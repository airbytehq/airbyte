# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""State writer implementation."""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING, NoReturn, final

from airbyte.shared.state_providers import StateProviderBase


if TYPE_CHECKING:
    from airbyte_protocol.models import AirbyteStateMessage


class StateWriterBase(StateProviderBase, abc.ABC):
    """A class to write state artifacts.

    This class is used to write state artifacts to a state store. It also serves as a provider
    of cached state artifacts.
    """

    def __init__(self) -> None:
        """Initialize the state writer."""
        self._latest_stream_state_messages: dict[str, AirbyteStateMessage] = {}
        """The latest state message seen for each stream."""

    @property
    def _state_message_artifacts(
        self,
    ) -> list[AirbyteStateMessage]:
        """Return all state artifacts."""
        return list(self._latest_stream_state_messages.values())

    @_state_message_artifacts.setter
    def _state_message_artifacts(self, value: list[AirbyteStateMessage]) -> NoReturn:
        """Override as no-op / not-implemented."""
        _ = value
        raise NotImplementedError("The `_state_message_artifacts` property cannot be set")

    @final
    def write_state(
        self,
        state_message: AirbyteStateMessage,
    ) -> None:
        """Save or 'write' a state artifact.

        This method is final and should not be overridden. Subclasses should instead overwrite
        the `_write_state` method.
        """
        if state_message.stream:
            self._latest_stream_state_messages[state_message.stream.stream_descriptor.name] = (
                state_message
            )

        self._write_state(state_message)

    @abc.abstractmethod
    def _write_state(
        self,
        state_message: AirbyteStateMessage,
    ) -> None:
        """Save or 'write' a state artifact."""
        ...


class StdOutStateWriter(StateWriterBase):
    """A state writer that writes state artifacts to stdout.

    This is useful when we want PyAirbyte to behave like a "Destination" in the Airbyte protocol.
    """

    def _write_state(
        self,
        state_message: AirbyteStateMessage,
    ) -> None:
        """Save or 'write' a state artifact."""
        print(state_message.model_dump_json())


class NoOpStateWriter(StateWriterBase):
    """A state writer that does not write state artifacts.

    Even though state messages are not sent anywhere, they are still stored in memory and
    can be accessed using the `state_message_artifacts` property and other methods inherited
    from the `StateProviderBase` class
    """

    def _write_state(
        self,
        state_message: AirbyteStateMessage,
    ) -> None:
        """Save or 'write' a state artifact."""
        _ = state_message
        pass
