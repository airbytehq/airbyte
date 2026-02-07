---
id: airbyte-sources-base
title: airbyte.sources.base
---

Module airbyte.sources.base
===========================
Base class implementation for sources.

Classes
-------

`Source(executor: Executor, name: str, config: dict[str, Any] | None = None, *, config_change_callback: ConfigChangeCallback | None = None, streams: str | list[str] | None = None, validate: bool = False, cursor_key_overrides: dict[str, str] | None = None, primary_key_overrides: dict[str, str | list[str]] | None = None)`
:   A class representing a source that can be called.
    
    Initialize the source.
    
    If config is provided, it will be validated against the spec if validate is True.

    ### Ancestors (in MRO)

    * airbyte._connector_base.ConnectorBase
    * abc.ABC

    ### Class variables

    `connector_type: Literal['destination', 'source']`
    :

    ### Instance variables

    `config_spec: dict[str, Any]`
    :   Generate a configuration spec for this connector, as a JSON Schema definition.
        
        This function generates a JSON Schema dictionary with configuration specs for the
        current connector, as a dictionary.
        
        Returns:
            dict: The JSON Schema configuration spec as a dictionary.

    `configured_catalog: ConfiguredAirbyteCatalog`
    :   Get the configured catalog for the given streams.
        
        If the raw catalog is not yet known, we call discover to get it.
        
        If no specific streams are selected, we return a catalog that syncs all available streams.
        
        TODO: We should consider disabling by default the streams that the connector would
        disable by default. (For instance, streams that require a premium license are sometimes
        disabled by default within the connector.)

    `discovered_catalog: AirbyteCatalog`
    :   Get the raw catalog for the given streams.
        
        If the catalog is not yet known, we call discover to get it.

    `docs_url: str`
    :   Get the URL to the connector's documentation.

    ### Methods

    `get_available_streams(self) ‑> list[str]`
    :   Get the available streams from the spec.

    `get_configured_catalog(self, streams: "Literal['*'] | list[str] | None" = None, *, force_full_refresh: bool = False) ‑> airbyte_protocol.models.airbyte_protocol.ConfiguredAirbyteCatalog`
    :   Get a configured catalog for the given streams.
        
        If no streams are provided, the selected streams will be used. If no streams are selected,
        all available streams will be used.
        
        If '*' is provided, all available streams will be used.
        
        If force_full_refresh is True, streams will be configured with full_refresh sync mode
        when supported by the stream. Otherwise, incremental sync mode is used when supported.

    `get_documents(self, stream: str, title_property: str | None = None, content_properties: list[str] | None = None, metadata_properties: list[str] | None = None, *, render_metadata: bool = False) ‑> Iterable[Document]`
    :   Read a stream from the connector and return the records as documents.
        
        If metadata_properties is not set, all properties that are not content will be added to
        the metadata.
        
        If render_metadata is True, metadata will be rendered in the document, as well as the
        the main content.

    `get_records(self, stream: str, *, limit: int | None = None, stop_event: threading.Event | None = None, normalize_field_names: bool = False, prune_undeclared_fields: bool = True) ‑> airbyte.datasets._lazy.LazyDataset`
    :   Read a stream from the connector.
        
        Args:
            stream: The name of the stream to read.
            limit: The maximum number of records to read. If None, all records will be read.
            stop_event: If set, the event can be triggered by the caller to stop reading records
                and terminate the process.
            normalize_field_names: When `True`, field names will be normalized to lower case, with
                special characters removed. This matches the behavior of PyAirbyte caches and most
                Airbyte destinations.
            prune_undeclared_fields: When `True`, undeclared fields will be pruned from the records,
                which generally matches the behavior of PyAirbyte caches and most Airbyte
                destinations, specifically when you expect the catalog may be stale. You can disable
                this to keep all fields in the records.
        
        This involves the following steps:
        * Call discover to get the catalog
        * Generate a configured catalog that syncs the given stream in full_refresh mode
        * Write the configured catalog and the config to a temporary file
        * execute the connector with read --config &lt;config_file&gt; --catalog &lt;catalog_file&gt;
        * Listen to the messages and return the first AirbyteRecordMessages that come along.
        * Make sure the subprocess is killed when the function returns.

    `get_samples(self, streams: "list[str] | Literal['*'] | None" = None, *, limit: int = 5, on_error: "Literal['raise', 'ignore', 'log']" = 'raise') ‑> dict[str, InMemoryDataset | None]`
    :   Get a sample of records from the given streams.

    `get_selected_streams(self) ‑> list[str]`
    :   Get the selected streams.
        
        If no streams are selected, return an empty list.

    `get_stream_json_schema(self, stream_name: str) ‑> dict[str, typing.Any]`
    :   Return the JSON Schema spec for the specified stream name.

    `print_samples(self, streams: "list[str] | Literal['*'] | None" = None, *, limit: int = 5, on_error: "Literal['raise', 'ignore', 'log']" = 'log') ‑> None`
    :   Print a sample of records from the given streams.

    `read(self, cache: CacheBase | None = None, *, streams: str | list[str] | None = None, write_strategy: str | WriteStrategy = WriteStrategy.AUTO, force_full_refresh: bool = False, skip_validation: bool = False) ‑> ReadResult`
    :   Read from the connector and write to the cache.
        
        Args:
            cache: The cache to write to. If not set, a default cache will be used.
            streams: Optional if already set. A list of stream names to select for reading. If set
                to "*", all streams will be selected.
            write_strategy: The strategy to use when writing to the cache. If a string, it must be
                one of "append", "merge", "replace", or "auto". If a WriteStrategy, it must be one
                of WriteStrategy.APPEND, WriteStrategy.MERGE, WriteStrategy.REPLACE, or
                WriteStrategy.AUTO.
            force_full_refresh: If True, the source will operate in full refresh mode. Otherwise,
                streams will be read in incremental mode if supported by the connector. This option
                must be True when using the "replace" strategy.
            skip_validation: If True, PyAirbyte will not pre-validate the input configuration before
                running the connector. This can be helpful in debugging, when you want to send
                configurations to the connector that otherwise might be rejected by JSON Schema
                validation rules.

    `select_all_streams(self) ‑> None`
    :   Select all streams.
        
        This is a more streamlined equivalent to:
        > source.select_streams(source.get_available_streams()).

    `select_streams(self, streams: str | list[str]) ‑> None`
    :   Select the stream names that should be read from the connector.
        
        Args:
            streams: A list of stream names to select. If set to "*", all streams will be selected.
        
        Currently, if this is not set, all streams will be read.

    `set_config(self, config: dict[str, Any], *, validate: bool = True) ‑> None`
    :   Set the config for the connector.
        
        If validate is True, raise an exception if the config fails validation.
        
        If validate is False, validation will be deferred until check() or validate_config()
        is called.

    `set_cursor_key(self, stream_name: str, cursor_key: str) ‑> None`
    :   Set the cursor for a single stream.
        
        Note:
        - This does not unset previously set cursors.
        - The cursor key must be a single field name.
        - Not all streams support custom cursors. If a stream does not support custom cursors,
          the override may be ignored.
        - Stream names are case insensitive, while field names are case sensitive.
        - Stream names are not validated by PyAirbyte. If the stream name
          does not exist in the catalog, the override may be ignored.

    `set_cursor_keys(self, **kwargs: str) ‑> None`
    :   Override the cursor key for one or more streams.
        
        Usage:
            source.set_cursor_keys(
                stream1="cursor1",
                stream2="cursor2",
            )
        
        Note:
        - This does not unset previously set cursors.
        - The cursor key must be a single field name.
        - Not all streams support custom cursors. If a stream does not support custom cursors,
          the override may be ignored.
        - Stream names are case insensitive, while field names are case sensitive.
        - Stream names are not validated by PyAirbyte. If the stream name
          does not exist in the catalog, the override may be ignored.

    `set_primary_key(self, stream_name: str, primary_key: str | list[str]) ‑> None`
    :   Set the primary key for a single stream.
        
        Note:
        - This does not unset previously set primary keys.
        - The primary key must be a single field name or a list of field names.
        - Not all streams support overriding primary keys. If a stream does not support overriding
          primary keys, the override may be ignored.
        - Stream names are case insensitive, while field names are case sensitive.
        - Stream names are not validated by PyAirbyte. If the stream name
          does not exist in the catalog, the override may be ignored.

    `set_primary_keys(self, **kwargs: str | list[str]) ‑> None`
    :   Override the primary keys for one or more streams.
        
        This does not unset previously set primary keys.
        
        Usage:
            source.set_primary_keys(
                stream1="pk1",
                stream2=["pk1", "pk2"],
            )
        
        Note:
        - This does not unset previously set primary keys.
        - The primary key must be a single field name or a list of field names.
        - Not all streams support overriding primary keys. If a stream does not support overriding
          primary keys, the override may be ignored.
        - Stream names are case insensitive, while field names are case sensitive.
        - Stream names are not validated by PyAirbyte. If the stream name
          does not exist in the catalog, the override may be ignored.

    `set_streams(self, streams: list[str]) ‑> None`
    :   Deprecated. See select_streams().