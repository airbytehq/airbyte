# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""State provider implementation."""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Literal

from airbyte_protocol.models import (
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStreamState,
)

from airbyte import exceptions as exc


if TYPE_CHECKING:
    from collections.abc import Iterable

    from airbyte_protocol.models import (
        AirbyteStateMessage,
        AirbyteStreamState,
    )


class StateProviderBase(abc.ABC):
    """A class to provide state artifacts."""

    @property
    @abc.abstractmethod
    def _state_message_artifacts(self) -> Iterable[AirbyteStateMessage]:
        """Generic internal interface to return all state artifacts.

        Subclasses should implement this property.
        """
        ...

    @property
    def stream_state_artifacts(
        self,
    ) -> list[AirbyteStreamState]:
        """Return all state artifacts.

        This is just a type guard around the private variable `_stream_state_artifacts` and the
        cast to `AirbyteStreamState` objects.
        """
        if self._state_message_artifacts is None:
            raise exc.PyAirbyteInternalError(message="No state artifacts were declared.")

        return [
            state_msg.stream
            for state_msg in self._state_message_artifacts
            if state_msg.type == AirbyteStateType.STREAM
        ]

    @property
    def state_message_artifacts(
        self,
    ) -> Iterable[AirbyteStreamState]:
        """Return all state artifacts.

        This is just a type guard around the private variable `_state_message_artifacts`.
        """
        result = self._state_message_artifacts
        if result is None:
            raise exc.PyAirbyteInternalError(message="No state artifacts were declared.")

        return result

    @property
    def known_stream_names(
        self,
    ) -> set[str]:
        """Return the unique set of all stream names with stored state."""
        return {state.stream_descriptor.name for state in self.stream_state_artifacts}

    def to_state_input_file_text(self) -> str:
        """Return the state artifacts as a JSON string.

        This is used when sending the state artifacts to the destination.
        """
        return (
            "["
            + "\n, ".join(
                [
                    state_artifact.model_dump_json()
                    for state_artifact in (self._state_message_artifacts or [])
                ]
            )
            + "]"
        )

    def get_stream_state(
        self,
        /,
        stream_name: str,
        not_found: None | AirbyteStateMessage | Literal["raise"] = "raise",
    ) -> AirbyteStateMessage:
        """Return the state message for the specified stream name."""
        for state_message in self.state_message_artifacts:
            if state_message.stream.stream_descriptor.name == stream_name:
                return state_message

        if not_found != "raise":
            return not_found

        raise exc.AirbyteStateNotFoundError(
            message="State message not found.",
            stream_name=stream_name,
            available_streams=list(self.known_stream_names),
        )


class StaticInputState(StateProviderBase):
    """A state manager that uses a static catalog state as input."""

    def __init__(
        self,
        from_state_messages: list[AirbyteStateMessage],
    ) -> None:
        """Initialize the state manager with a static catalog state."""
        self._state_messages: list[AirbyteStateMessage] = from_state_messages

    @property
    def _state_message_artifacts(self) -> Iterable[AirbyteStateMessage]:
        return self._state_messages


class JoinedStateProvider(StateProviderBase):
    """A state provider that joins two state providers."""

    def __init__(
        self,
        /,
        primary: StateProviderBase,
        secondary: StateProviderBase,
    ) -> None:
        """Initialize the state provider with two state providers."""
        self._primary_state_provider = primary
        self._secondary_state_provider = secondary

    @property
    def known_stream_names(
        self,
    ) -> set[str]:
        """Return the unique set of all stream names with stored state."""
        return (
            self._primary_state_provider.known_stream_names
            | self._secondary_state_provider.known_stream_names
        )

    @property
    def _state_message_artifacts(self) -> Iterable[AirbyteStateMessage]:
        """Return all state artifacts."""
        for stream_name in self.known_stream_names:
            state: AirbyteStateMessage = self._primary_state_provider.get_stream_state(
                stream_name,
                self._secondary_state_provider.get_stream_state(
                    stream_name,
                    None,
                ),
            )
            if state:
                yield state
