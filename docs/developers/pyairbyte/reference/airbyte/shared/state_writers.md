---
id: airbyte-shared-state_writers
title: airbyte.shared.state_writers
---

Module airbyte.shared.state_writers
===================================
State writer implementation.

Classes
-------

`NoOpStateWriter()`
:   A state writer that does not write state artifacts.
    
    Even though state messages are not sent anywhere, they are still stored in memory and
    can be accessed using the `state_message_artifacts` property and other methods inherited
    from the `StateProviderBase` class
    
    Initialize the state writer.

    ### Ancestors (in MRO)

    * airbyte.shared.state_writers.StateWriterBase
    * airbyte.shared.state_providers.StateProviderBase
    * abc.ABC

`StateWriterBase()`
:   A class to write state artifacts.
    
    This class is used to write state artifacts to a state store. It also serves as a provider
    of cached state artifacts.
    
    Initialize the state writer.

    ### Ancestors (in MRO)

    * airbyte.shared.state_providers.StateProviderBase
    * abc.ABC

    ### Descendants

    * airbyte.caches._state_backend.SqlStateWriter
    * airbyte.shared.state_writers.NoOpStateWriter
    * airbyte.shared.state_writers.StdOutStateWriter

    ### Methods

    `write_state(self, state_message: AirbyteStateMessage) ‑> None`
    :   Save or 'write' a state artifact.
        
        This method is final and should not be overridden. Subclasses should instead overwrite
        the `_write_state` method.

`StdOutStateWriter()`
:   A state writer that writes state artifacts to stdout.
    
    This is useful when we want PyAirbyte to behave like a "Destination" in the Airbyte protocol.
    
    Initialize the state writer.

    ### Ancestors (in MRO)

    * airbyte.shared.state_writers.StateWriterBase
    * airbyte.shared.state_providers.StateProviderBase
    * abc.ABC