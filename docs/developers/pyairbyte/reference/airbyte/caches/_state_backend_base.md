---
sidebar_label: _state_backend_base
title: airbyte.caches._state_backend_base
---

State backend implementation.

## annotations

## abc

## TYPE\_CHECKING

## StateBackendBase Objects

```python
class StateBackendBase(abc.ABC)
```

A class which manages the stream state for data synced.

The backend is responsible for storing and retrieving the state of streams. It generates
`StateProvider` objects, which are paired to a specific source and table prefix.

#### \_sql\_config

#### \_\_init\_\_

```python
def __init__() -> None
```

Initialize the state manager with a static catalog state.

#### get\_state\_provider

```python
@abc.abstractmethod
def get_state_provider(
        source_name: str,
        table_prefix: str,
        *,
        refresh: bool = True,
        destination_name: str | None = None) -> StateProviderBase
```

Return the state provider.

#### get\_state\_writer

```python
@abc.abstractmethod
def get_state_writer(source_name: str,
                     destination_name: str | None = None) -> StateWriterBase
```

Return a state writer for a named source.

The same table prefix of the backend will be used for the state writer.

#### \_initialize\_backend

```python
def _initialize_backend(*, force_refresh: bool = False) -> None
```

Do any needed initialization, for instance to load state artifacts from the cache.

By default, this method does nothing. Base classes may override this method to load state
artifacts or perform other initialization tasks.

