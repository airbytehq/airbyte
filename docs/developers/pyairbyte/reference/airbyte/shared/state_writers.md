---
sidebar_label: state_writers
title: airbyte.shared.state_writers
---

State writer implementation.

## annotations

## abc

## TYPE\_CHECKING

## NoReturn

## final

## StateProviderBase

## StateWriterBase Objects

```python
class StateWriterBase(StateProviderBase, abc.ABC)
```

A class to write state artifacts.

This class is used to write state artifacts to a state store. It also serves as a provider
of cached state artifacts.

#### \_\_init\_\_

```python
def __init__() -> None
```

Initialize the state writer.

#### \_state\_message\_artifacts

```python
@property
def _state_message_artifacts() -> list[AirbyteStateMessage]
```

Return all state artifacts.

#### \_state\_message\_artifacts

```python
@_state_message_artifacts.setter
def _state_message_artifacts(value: list[AirbyteStateMessage]) -> NoReturn
```

Override as no-op / not-implemented.

#### write\_state

```python
@final
def write_state(state_message: AirbyteStateMessage) -> None
```

Save or &#x27;write&#x27; a state artifact.

This method is final and should not be overridden. Subclasses should instead overwrite
the `_write_state` method.

#### \_write\_state

```python
@abc.abstractmethod
def _write_state(state_message: AirbyteStateMessage) -> None
```

Save or &#x27;write&#x27; a state artifact.

## StdOutStateWriter Objects

```python
class StdOutStateWriter(StateWriterBase)
```

A state writer that writes state artifacts to stdout.

This is useful when we want PyAirbyte to behave like a &quot;Destination&quot; in the Airbyte protocol.

#### \_write\_state

```python
def _write_state(state_message: AirbyteStateMessage) -> None
```

Save or &#x27;write&#x27; a state artifact.

## NoOpStateWriter Objects

```python
class NoOpStateWriter(StateWriterBase)
```

A state writer that does not write state artifacts.

Even though state messages are not sent anywhere, they are still stored in memory and
can be accessed using the `state_message_artifacts` property and other methods inherited
from the `StateProviderBase` class

#### \_write\_state

```python
def _write_state(state_message: AirbyteStateMessage) -> None
```

Save or &#x27;write&#x27; a state artifact.

