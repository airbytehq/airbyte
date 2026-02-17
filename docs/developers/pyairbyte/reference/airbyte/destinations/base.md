---
id: airbyte-destinations-base
title: airbyte.destinations.base
---

Module airbyte.destinations.base
================================
Destination base classes.

For usage examples, see the `airbyte.destinations` module documentation.

Classes
-------

`Destination(executor: Executor, name: str, config: dict[str, Any] | None = None, *, config_change_callback: ConfigChangeCallback | None = None, validate: bool = False)`
:   A class representing a destination that can be called.
    
    Initialize the source.
    
    If config is provided, it will be validated against the spec if validate is True.

    ### Ancestors (in MRO)

    * airbyte._connector_base.ConnectorBase
    * airbyte._writers.base.AirbyteWriterInterface
    * abc.ABC

    ### Class variables

    `connector_type: Literal['destination', 'source']`
    :

    ### Methods

    `write(self, source_data: Source | ReadResult, *, streams: "list[str] | Literal['*'] | None" = None, cache: CacheBase | Literal[False] | None = None, state_cache: CacheBase | Literal[False] | None = None, write_strategy: WriteStrategy = WriteStrategy.AUTO, force_full_refresh: bool = False) ‑> WriteResult`
    :   Write data from source connector or already cached source data.
        
        Caching is enabled by default, unless explicitly disabled.
        
        Args:
            source_data: The source data to write. Can be a `Source` or a `ReadResult` object.
            streams: The streams to write to the destination. If omitted or if "*" is provided,
                all streams will be written. If `source_data` is a source, then streams must be
                selected here or on the source. If both are specified, this setting will override
                the stream selection on the source.
            cache: The cache to use for reading source_data. If `None`, no cache will be used. If
                False, the cache will be disabled. This must be `None` if `source_data` is already
                a `Cache` object.
            state_cache: A cache to use for storing incremental state. You do not need to set this
                if `cache` is specified or if `source_data` is a `Cache` object. Set to `False` to
                disable state management.
            write_strategy: The strategy to use for writing source_data. If `AUTO`, the connector
                will decide the best strategy to use.
            force_full_refresh: Whether to force a full refresh of the source_data. If `True`, any
                existing state will be ignored and all source data will be reloaded.
        
        For incremental syncs, `cache` or `state_cache` will be checked for matching state values.
        If the cache has tracked state, this will be used for the sync. Otherwise, if there is
        a known destination state, the destination-specific state will be used. If neither are
        available, a full refresh will be performed.