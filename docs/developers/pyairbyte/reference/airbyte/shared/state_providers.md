---
id: airbyte-shared-state_providers
title: "airbyte.shared.state_providers Module"
sidebar_label: "airbyte.shared.state_providers"
toc_max_heading_level: 5
---

# `airbyte.shared.state_providers` Module

State provider implementation.

### `JoinedStateProvider` {#airbyte.shared.state_providers.JoinedStateProvider}

<ApiMember kind="class">

<ApiSignature>

```python
class JoinedStateProvider(
    primary: StateProviderBase,
    secondary: StateProviderBase,
)
```

</ApiSignature>

A state provider that joins two state providers.

Initialize the state provider with two state providers.

#### Bases {#airbyte.shared.state_providers.JoinedStateProvider--bases}

`airbyte.shared.state_providers.StateProviderBase`

</ApiMember>

### `StateProviderBase` {#airbyte.shared.state_providers.StateProviderBase}

<ApiMember kind="class">

<ApiSignature>

```python
class StateProviderBase()
```

</ApiSignature>

A class to provide state artifacts.

#### Bases {#airbyte.shared.state_providers.StateProviderBase--bases}

`abc.ABC`
#### Descendants {#airbyte.shared.state_providers.StateProviderBase--descendants}

`airbyte.shared.state_providers.JoinedStateProvider`, `airbyte.shared.state_providers.StaticInputState`, `airbyte.shared.state_writers.StateWriterBase`
#### Instance Variables {#airbyte.shared.state_providers.StateProviderBase--instance-variables}

- **`known_stream_names`**&nbsp;(`set[str]`)

  Return the unique set of all stream names with stored state.

- **`state_message_artifacts`**&nbsp;(`Iterable[AirbyteStreamState]`)

  Return all state artifacts.

  This is just a type guard around the private variable `_state_message_artifacts`.

- **`stream_state_artifacts`**&nbsp;(`list[AirbyteStreamState]`)

  Return all state artifacts.

  This is just a type guard around the private variable `_stream_state_artifacts` and the
  cast to `AirbyteStreamState` objects.

#### Methods {#airbyte.shared.state_providers.StateProviderBase--methods}

##### `get_stream_state` {#airbyte.shared.state_providers.StateProviderBase.get_stream_state}

<ApiMember kind="method">

<ApiSignature>

```python
def get_stream_state(
    self,
    /,
    stream_name: str,
    not_found: "AirbyteStateMessage | Literal['raise'] | None" = 'raise',
) -> airbyte_protocol.models.airbyte_protocol.AirbyteStateMessage
```

</ApiSignature>

Return the state message for the specified stream name.

</ApiMember>

##### `to_state_input_file_text` {#airbyte.shared.state_providers.StateProviderBase.to_state_input_file_text}

<ApiMember kind="method">

<ApiSignature>

```python
def to_state_input_file_text(self) -> str
```

</ApiSignature>

Return the state artifacts as a JSON string.

This is used when sending the state artifacts to the destination.

</ApiMember>

</ApiMember>

### `StaticInputState` {#airbyte.shared.state_providers.StaticInputState}

<ApiMember kind="class">

<ApiSignature>

```python
class StaticInputState(from_state_messages: list[AirbyteStateMessage])
```

</ApiSignature>

A state manager that uses a static catalog state as input.

Initialize the state manager with a static catalog state.

#### Bases {#airbyte.shared.state_providers.StaticInputState--bases}

`airbyte.shared.state_providers.StateProviderBase`

</ApiMember>