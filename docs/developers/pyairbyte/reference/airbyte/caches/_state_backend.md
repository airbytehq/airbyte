---
sidebar_label: _state_backend
title: airbyte.caches._state_backend
---

State backend implementation.

## annotations

## datetime

## timezone

## TYPE\_CHECKING

## Column

## DateTime

## PrimaryKeyConstraint

## String

## and\_

## Session

## declarative\_base

## AirbyteStateMessage

## AirbyteStateType

## StateBackendBase

## PyAirbyteInputError

## PyAirbyteInternalError

## StaticInputState

## StateWriterBase

#### CACHE\_STATE\_TABLE\_NAME

#### DESTINATION\_STATE\_TABLE\_NAME

#### GLOBAL\_STATE\_STREAM\_NAME

#### LEGACY\_STATE\_STREAM\_NAME

#### GLOBAL\_STATE\_STREAM\_NAMES

#### SqlAlchemyModel

A base class to use for SQLAlchemy ORM models.

## CacheStreamStateModel Objects

```python
class CacheStreamStateModel(SqlAlchemyModel)
```

A SQLAlchemy ORM model to store state metadata for internal caches.

#### \_\_tablename\_\_

#### source\_name

The source name.

#### stream\_name

The stream name.

#### table\_name

The table name holding records for the stream.

#### state\_json

The JSON string representation of the state message.

#### last\_updated

The last time the state was updated.

## DestinationStreamStateModel Objects

```python
class DestinationStreamStateModel(SqlAlchemyModel)
```

A SQLAlchemy ORM model to store state metadata for destinations.

This is a separate table from the cache state table. The destination state table
includes a `destination_name` column to allow multiple destinations to share the same,
and it excludes `table_name`, since we don&#x27;t necessarily have visibility into the destination&#x27;s
internal table naming conventions.

#### \_\_tablename\_\_

#### \_\_table\_args\_\_

#### destination\_name

The destination name.

#### source\_name

The source name.

#### stream\_name

The stream name.

#### state\_json

The JSON string representation of the state message.

#### last\_updated

The last time the state was updated.

## SqlStateWriter Objects

```python
class SqlStateWriter(StateWriterBase)
```

State writer for SQL backends.

#### \_\_init\_\_

```python
def __init__(source_name: str,
             backend: SqlStateBackend,
             *,
             destination_name: str | None = None) -> None
```

Initialize the state writer.

**Arguments**:

- `source_name` - The name of the source.
- `backend` - The state backend.
- `destination_name` - The name of the destination, if writing to a destination. Otherwise,
  this should be `None` to write state for the PyAirbyte cache itself.

#### \_write\_state

```python
def _write_state(state_message: AirbyteStateMessage) -> None
```

## SqlStateBackend Objects

```python
class SqlStateBackend(StateBackendBase)
```

A class to manage the stream catalog of data synced to a cache.

This includes:
- What streams exist and to what tables they map
- The JSON schema for each stream

#### \_\_init\_\_

```python
def __init__(sql_config: SqlConfig, table_prefix: str = "") -> None
```

Initialize the state manager with a static catalog state.

#### \_ensure\_internal\_tables

```python
def _ensure_internal_tables() -> None
```

Ensure the internal tables exist in the SQL database.

#### get\_state\_provider

```python
def get_state_provider(
        source_name: str,
        table_prefix: str = "",
        streams_filter: list[str] | None = None,
        *,
        refresh: bool = True,
        destination_name: str | None = None) -> StateProviderBase
```

Return the state provider.

#### get\_state\_writer

```python
def get_state_writer(source_name: str,
                     destination_name: str | None = None) -> StateWriterBase
```

Return a state writer for a named source.

**Arguments**:

- `source_name` - The name of the source.
- `destination_name` - The name of the destination, if writing to a destination. Otherwise,
  this should be `None` to write state for the PyAirbyte cache itself.

