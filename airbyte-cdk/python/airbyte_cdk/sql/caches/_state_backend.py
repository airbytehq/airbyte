# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""State backend implementation."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pytz import utc
from sqlalchemy import Column, DateTime, PrimaryKeyConstraint, String, and_
from sqlalchemy.orm import Session, declarative_base

from airbyte_cdk.models import (
    AirbyteStateMessage,
    AirbyteStateType,
)

from airbyte_cdk.sql.caches._state_backend_base import (
    StateBackendBase,
)
from airbyte_cdk.sql.exceptions import PyAirbyteInputError, PyAirbyteInternalError
from airbyte_cdk.sql.state_providers import StaticInputState
from airbyte_cdk.sql.state_writers import StateWriterBase


if TYPE_CHECKING:
    from sqlalchemy.engine import Engine

    from airbyte_cdk.sql.state_providers import StateProviderBase


CACHE_STATE_TABLE_NAME = "_airbyte_state"
DESTINATION_STATE_TABLE_NAME = "_airbyte_destination_state"

GLOBAL_STATE_STREAM_NAME = "_GLOBAL"
LEGACY_STATE_STREAM_NAME = "_LEGACY"
GLOBAL_STATE_STREAM_NAMES = [GLOBAL_STATE_STREAM_NAME, LEGACY_STATE_STREAM_NAME]


SqlAlchemyModel: type = declarative_base()
"""A base class to use for SQLAlchemy ORM models."""


class CacheStreamStateModel(SqlAlchemyModel):  # type: ignore[misc]
    """A SQLAlchemy ORM model to store state metadata for internal caches."""

    __tablename__ = CACHE_STATE_TABLE_NAME

    source_name = Column(String)
    """The source name."""

    stream_name = Column(String)
    """The stream name."""

    table_name = Column(String, primary_key=True)
    """The table name holding records for the stream."""

    state_json = Column(String)
    """The JSON string representation of the state message."""

    last_updated = Column(
        DateTime(timezone=True), onupdate=datetime.now(utc), default=datetime.now(utc)
    )
    """The last time the state was updated."""


class DestinationStreamStateModel(SqlAlchemyModel):  # type: ignore[misc]
    """A SQLAlchemy ORM model to store state metadata for destinations.

    This is a separate table from the cache state table. The destination state table
    includes a `destination_name` column to allow multiple destinations to share the same,
    and it excludes `table_name`, since we don't necessarily have visibility into the destination's
    internal table naming conventions.
    """

    __tablename__ = DESTINATION_STATE_TABLE_NAME
    __table_args__ = (PrimaryKeyConstraint("destination_name", "source_name", "stream_name"),)

    destination_name = Column(String, nullable=False)
    """The destination name."""

    source_name = Column(String, nullable=False)
    """The source name."""

    stream_name = Column(String, nullable=False)
    """The stream name."""

    state_json = Column(String)
    """The JSON string representation of the state message."""

    last_updated = Column(
        DateTime(timezone=True), onupdate=datetime.now(utc), default=datetime.now(utc)
    )
    """The last time the state was updated."""


class SqlStateWriter(StateWriterBase):
    """State writer for SQL backends."""

    def __init__(
        self,
        source_name: str,
        backend: SqlStateBackend,
        *,
        destination_name: str | None = None,
    ) -> None:
        """Initialize the state writer.

        Args:
            source_name: The name of the source.
            backend: The state backend.
            destination_name: The name of the destination, if writing to a destination. Otherwise,
                this should be `None` to write state for the PyAirbyte cache itself.
        """
        self._state_backend: SqlStateBackend = backend
        self.source_name: str = source_name
        self.destination_name: str | None = destination_name
        super().__init__()

    def _write_state(
        self,
        state_message: AirbyteStateMessage,
    ) -> None:
        if state_message.type == AirbyteStateType.GLOBAL:
            stream_name = GLOBAL_STATE_STREAM_NAME
        if state_message.type == AirbyteStateType.LEGACY:
            stream_name = LEGACY_STATE_STREAM_NAME
        elif state_message.type == AirbyteStateType.STREAM and state_message.stream:
            stream_name = state_message.stream.stream_descriptor.name
        else:
            raise PyAirbyteInternalError(
                message="Invalid state message type.",
                context={"state_message": state_message},
            )

        self._state_backend._ensure_internal_tables()  # noqa: SLF001  # Non-public member access
        table_prefix = self._state_backend._table_prefix  # noqa: SLF001
        engine = self._state_backend._engine  # noqa: SLF001

        # Calculate the new state model to write.
        new_state = (
            DestinationStreamStateModel(
                destination_name=self.destination_name,
                source_name=self.source_name,
                stream_name=stream_name,
                state_json=state_message.model_dump_json(),
            )
            if self.destination_name
            else CacheStreamStateModel(
                source_name=self.source_name,
                stream_name=stream_name,
                table_name=table_prefix + stream_name,
                state_json=state_message.model_dump_json(),
            )
        )

        # Now write the new state to the database.
        with Session(engine) as session:
            # First, delete the existing state for the stream.
            if self.destination_name:
                session.query(DestinationStreamStateModel).filter(
                    and_(
                        (DestinationStreamStateModel.destination_name == self.destination_name),
                        (DestinationStreamStateModel.source_name == self.source_name),
                        (DestinationStreamStateModel.stream_name == stream_name),
                    )
                ).delete()
            else:
                session.query(CacheStreamStateModel).filter(
                    CacheStreamStateModel.table_name == table_prefix + stream_name
                ).delete()

            # This commit prevents "duplicate key" errors but (in theory) should not be necessary.
            session.commit()
            session.add(new_state)
            session.commit()


class SqlStateBackend(StateBackendBase):
    """A class to manage the stream catalog of data synced to a cache.

    This includes:
    - What streams exist and to what tables they map
    - The JSON schema for each stream
    """

    def __init__(
        self,
        engine: Engine,
        table_prefix: str = "",
    ) -> None:
        """Initialize the state manager with a static catalog state."""
        self._engine: Engine = engine
        self._table_prefix = table_prefix
        super().__init__()

    def _ensure_internal_tables(self) -> None:
        """Ensure the internal tables exist in the SQL database."""
        engine = self._engine
        SqlAlchemyModel.metadata.create_all(engine)  # type: ignore[attr-defined]

    def get_state_provider(
        self,
        source_name: str,
        table_prefix: str = "",
        streams_filter: list[str] | None = None,
        *,
        refresh: bool = True,
        destination_name: str | None = None,
    ) -> StateProviderBase:
        """Return the state provider."""
        if destination_name and table_prefix:
            raise PyAirbyteInputError(
                message="Both 'destination_name' and 'table_prefix' cannot be set at the same time."
            )

        _ = refresh  # Always refresh the state (for now)
        self._ensure_internal_tables()

        if destination_name:
            stream_state_model = DestinationStreamStateModel
        else:
            stream_state_model = CacheStreamStateModel

        engine = self._engine
        with Session(engine) as session:
            query = session.query(stream_state_model).filter(
                stream_state_model.source_name == source_name
                and (
                    stream_state_model.table_name.startswith(table_prefix)
                    or stream_state_model.stream_name.in_(GLOBAL_STATE_STREAM_NAMES)
                )
            )
            if destination_name:
                query = query.filter(stream_state_model.destination_name == destination_name)
            if streams_filter:
                query = query.filter(
                    stream_state_model.stream_name.in_(
                        [*streams_filter, *GLOBAL_STATE_STREAM_NAMES]
                    )
                )
            states: list = query.all()
            if not destination_name:
                # When returning cache states, exclude any states where the table name would not
                # match what the current cache table prefixes would generate. These are logically
                # part of a different cache, since each cache uses its own table prefix.
                states = [
                    state
                    for state in states
                    if state.table_name == table_prefix + state.stream_name
                ]

        return StaticInputState(
            from_state_messages=[
                AirbyteStateMessage.model_validate_json(state.state_json) for state in states
            ]
        )

    def get_state_writer(
        self,
        source_name: str,
        destination_name: str | None = None,
    ) -> StateWriterBase:
        """Return a state writer for a named source.

        Args:
            source_name: The name of the source.
            destination_name: The name of the destination, if writing to a destination. Otherwise,
                this should be `None` to write state for the PyAirbyte cache itself.
        """
        return SqlStateWriter(
            source_name=source_name,
            backend=self,
            destination_name=destination_name,
        )
