---
id: airbyte-shared-state_writers
title: "airbyte.shared.state_writers Module"
sidebar_label: "airbyte.shared.state_writers"
toc_max_heading_level: 5
---

# `airbyte.shared.state_writers` Module

State writer implementation.

### `NoOpStateWriter` {#airbyte.shared.state_writers.NoOpStateWriter}

<ApiMember kind="class">

<ApiSignature>

```python
class NoOpStateWriter()
```

</ApiSignature>

A state writer that does not write state artifacts.

Even though state messages are not sent anywhere, they are still stored in memory and
can be accessed using the `state_message_artifacts` property and other methods inherited
from the `StateProviderBase` class

Initialize the state writer.

#### Bases {#airbyte.shared.state_writers.NoOpStateWriter--bases}

`airbyte.shared.state_writers.StateWriterBase`

</ApiMember>

### `StateWriterBase` {#airbyte.shared.state_writers.StateWriterBase}

<ApiMember kind="class">

<ApiSignature>

```python
class StateWriterBase()
```

</ApiSignature>

A class to write state artifacts.

This class is used to write state artifacts to a state store. It also serves as a provider
of cached state artifacts.

Initialize the state writer.

#### Bases {#airbyte.shared.state_writers.StateWriterBase--bases}

`airbyte.shared.state_providers.StateProviderBase`, `abc.ABC`
#### Descendants {#airbyte.shared.state_writers.StateWriterBase--descendants}

`airbyte.caches._state_backend.SqlStateWriter`, `airbyte.shared.state_writers.NoOpStateWriter`, `airbyte.shared.state_writers.StdOutStateWriter`
#### Methods {#airbyte.shared.state_writers.StateWriterBase--methods}

#### `write_state` {#airbyte.shared.state_writers.StateWriterBase.write_state}

<ApiMember kind="method">

<ApiSignature>

```python
def write_state(self, state_message: AirbyteStateMessage) -> None
```

</ApiSignature>

Save or 'write' a state artifact.

This method is final and should not be overridden. Subclasses should instead overwrite
the `_write_state` method.

</ApiMember>

</ApiMember>

### `StdOutStateWriter` {#airbyte.shared.state_writers.StdOutStateWriter}

<ApiMember kind="class">

<ApiSignature>

```python
class StdOutStateWriter()
```

</ApiSignature>

A state writer that writes state artifacts to stdout.

This is useful when we want PyAirbyte to behave like a "Destination" in the Airbyte protocol.

Initialize the state writer.

#### Bases {#airbyte.shared.state_writers.StdOutStateWriter--bases}

`airbyte.shared.state_writers.StateWriterBase`

</ApiMember>