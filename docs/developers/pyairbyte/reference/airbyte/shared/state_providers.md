---
sidebar_label: state_providers
title: airbyte.shared.state_providers
---

State provider implementation.

## annotations

## abc

## TYPE\_CHECKING

## Literal

## AirbyteStateMessage

## AirbyteStateType

## AirbyteStreamState

## exc

## StateProviderBase Objects

```python
class StateProviderBase(abc.ABC)
```

A class to provide state artifacts.

#### \_state\_message\_artifacts

```python
@property
@abc.abstractmethod
def _state_message_artifacts() -> Iterable[AirbyteStateMessage]
```

Generic internal interface to return all state artifacts.

Subclasses should implement this property.

#### stream\_state\_artifacts

```python
@property
def stream_state_artifacts() -> list[AirbyteStreamState]
```

Return all state artifacts.

This is just a type guard around the private variable `_stream_state_artifacts` and the
cast to `AirbyteStreamState` objects.

#### state\_message\_artifacts

```python
@property
def state_message_artifacts() -> Iterable[AirbyteStreamState]
```

Return all state artifacts.

This is just a type guard around the private variable `_state_message_artifacts`.

#### known\_stream\_names

```python
@property
def known_stream_names() -> set[str]
```

Return the unique set of all stream names with stored state.

#### to\_state\_input\_file\_text

```python
def to_state_input_file_text() -> str
```

Return the state artifacts as a JSON string.

This is used when sending the state artifacts to the destination.

#### get\_stream\_state

```python
def get_stream_state(
    stream_name: str,
    not_found: AirbyteStateMessage | Literal["raise"] | None = "raise"
) -> AirbyteStateMessage
```

Return the state message for the specified stream name.

## StaticInputState Objects

```python
class StaticInputState(StateProviderBase)
```

A state manager that uses a static catalog state as input.

#### \_\_init\_\_

```python
def __init__(from_state_messages: list[AirbyteStateMessage]) -> None
```

Initialize the state manager with a static catalog state.

#### \_state\_message\_artifacts

```python
@property
def _state_message_artifacts() -> Iterable[AirbyteStateMessage]
```

## JoinedStateProvider Objects

```python
class JoinedStateProvider(StateProviderBase)
```

A state provider that joins two state providers.

#### \_\_init\_\_

```python
def __init__(primary: StateProviderBase, secondary: StateProviderBase) -> None
```

Initialize the state provider with two state providers.

#### known\_stream\_names

```python
@property
def known_stream_names() -> set[str]
```

Return the unique set of all stream names with stored state.

#### \_state\_message\_artifacts

```python
@property
def _state_message_artifacts() -> Iterable[AirbyteStateMessage]
```

Return all state artifacts.

