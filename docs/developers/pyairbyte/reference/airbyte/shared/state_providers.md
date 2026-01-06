---
id: airbyte-shared-state_providers
title: airbyte.shared.state_providers
---

Module airbyte.shared.state_providers
=====================================
State provider implementation.

Classes
-------

`JoinedStateProvider(primary: StateProviderBase, secondary: StateProviderBase)`
:   A state provider that joins two state providers.
    
    Initialize the state provider with two state providers.

    ### Ancestors (in MRO)

    * airbyte.shared.state_providers.StateProviderBase
    * abc.ABC

`StateProviderBase()`
:   A class to provide state artifacts.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * airbyte.shared.state_providers.JoinedStateProvider
    * airbyte.shared.state_providers.StaticInputState
    * airbyte.shared.state_writers.StateWriterBase

    ### Instance variables

    `known_stream_names: set[str]`
    :   Return the unique set of all stream names with stored state.

    `state_message_artifacts: Iterable[AirbyteStreamState]`
    :   Return all state artifacts.
        
        This is just a type guard around the private variable `_state_message_artifacts`.

    `stream_state_artifacts: list[AirbyteStreamState]`
    :   Return all state artifacts.
        
        This is just a type guard around the private variable `_stream_state_artifacts` and the
        cast to `AirbyteStreamState` objects.

    ### Methods

    `get_stream_state(self, /, stream_name: str, not_found: "AirbyteStateMessage | Literal['raise'] | None" = 'raise') ‑> airbyte_protocol.models.airbyte_protocol.AirbyteStateMessage`
    :   Return the state message for the specified stream name.

    `to_state_input_file_text(self) ‑> str`
    :   Return the state artifacts as a JSON string.
        
        This is used when sending the state artifacts to the destination.

`StaticInputState(from_state_messages: list[AirbyteStateMessage])`
:   A state manager that uses a static catalog state as input.
    
    Initialize the state manager with a static catalog state.

    ### Ancestors (in MRO)

    * airbyte.shared.state_providers.StateProviderBase
    * abc.ABC