Module airbyte_cdk.sources.singer.singer_helpers
================================================

Functions
---------

    
`configured_for_incremental(configured_stream: airbyte_cdk.models.airbyte_protocol.ConfiguredAirbyteStream)`
:   

    
`get_stream_level_metadata(metadatas: List[Dict[str, Any]]) ‑> Optional[Dict[str, Any]]`
:   

    
`is_field_metadata(metadata)`
:   

    
`override_sync_modes(airbyte_stream: airbyte_cdk.models.airbyte_protocol.AirbyteStream, overrides: airbyte_cdk.sources.singer.singer_helpers.SyncModeInfo)`
:   

    
`set_sync_modes_from_metadata(airbyte_stream: airbyte_cdk.models.airbyte_protocol.AirbyteStream, metadatas: List[Dict[str, Any]])`
:   

    
`to_json(string)`
:   

Classes
-------

`Catalogs(singer_catalog: object, airbyte_catalog: airbyte_cdk.models.airbyte_protocol.AirbyteCatalog)`
:   Catalogs(singer_catalog: object, airbyte_catalog: airbyte_cdk.models.airbyte_protocol.AirbyteCatalog)

    ### Class variables

    `airbyte_catalog: airbyte_cdk.models.airbyte_protocol.AirbyteCatalog`
    :

    `singer_catalog: object`
    :

`SingerHelper()`
:   

    ### Static methods

    `create_singer_catalog_with_selection(masked_airbyte_catalog: airbyte_cdk.models.airbyte_protocol.ConfiguredAirbyteCatalog, discovered_singer_catalog: object) ‑> str`
    :

    `get_catalogs(logger, shell_command: str, sync_mode_overrides: Dict[str, airbyte_cdk.sources.singer.singer_helpers.SyncModeInfo], primary_key_overrides: Dict[str, List[str]], excluded_streams: List) ‑> airbyte_cdk.sources.singer.singer_helpers.Catalogs`
    :

    `read(logger, shell_command, is_message=<function SingerHelper.<lambda>>) ‑> Iterator[airbyte_cdk.models.airbyte_protocol.AirbyteMessage]`
    :

    `singer_catalog_to_airbyte_catalog(singer_catalog: Dict[str, Any], sync_mode_overrides: Dict[str, airbyte_cdk.sources.singer.singer_helpers.SyncModeInfo], primary_key_overrides: Dict[str, List[str]]) ‑> airbyte_cdk.models.airbyte_protocol.AirbyteCatalog`
    :   :param singer_catalog:
        :param sync_mode_overrides: A dict from stream name to the sync modes it should use. Each stream in this dict must exist in the Singer catalog,
          but not every stream in the catalog should exist in this
        :param primary_key_overrides: A dict of stream name -> list of fields to be used as PKs.
        :return: Airbyte Catalog

`SyncModeInfo(supported_sync_modes: Optional[List[airbyte_cdk.models.airbyte_protocol.SyncMode]] = None, source_defined_cursor: Optional[bool] = None, default_cursor_field: Optional[List[str]] = None)`
:   SyncModeInfo(supported_sync_modes: Optional[List[airbyte_cdk.models.airbyte_protocol.SyncMode]] = None, source_defined_cursor: Optional[bool] = None, default_cursor_field: Optional[List[str]] = None)

    ### Class variables

    `default_cursor_field: Optional[List[str]]`
    :

    `source_defined_cursor: Optional[bool]`
    :

    `supported_sync_modes: Optional[List[airbyte_cdk.models.airbyte_protocol.SyncMode]]`
    :