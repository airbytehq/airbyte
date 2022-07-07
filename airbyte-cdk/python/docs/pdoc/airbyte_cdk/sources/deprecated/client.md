Module airbyte_cdk.sources.deprecated.client
============================================

Functions
---------

    
`configured_catalog_from_client(client: airbyte_cdk.sources.deprecated.client.BaseClient) ‑> airbyte_cdk.models.airbyte_protocol.ConfiguredAirbyteCatalog`
:   Helper to generate configured catalog for testing

    
`package_name_from_class(cls: object) ‑> str`
:   Find the package name given a class name

Classes
-------

`BaseClient(**kwargs)`
:   Base client for API

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.deprecated.client.StreamStateMixin
    * abc.ABC

    ### Class variables

    `schema_loader_class`
    :   JSONSchema loader from package resources

    ### Instance variables

    `streams: Generator[airbyte_cdk.models.airbyte_protocol.AirbyteStream, None, None]`
    :   List of available streams

    ### Methods

    `health_check(self) ‑> Tuple[bool, str]`
    :   Check if service is up and running

    `read_stream(self, stream: airbyte_cdk.models.airbyte_protocol.AirbyteStream) ‑> Generator[Dict[str, Any], None, None]`
    :   Yield records from stream

`StreamStateMixin()`
:   

    ### Descendants

    * airbyte_cdk.sources.deprecated.client.BaseClient

    ### Methods

    `get_stream_state(self, name: str) ‑> Any`
    :   Get state of stream with corresponding name

    `set_stream_state(self, name: str, state: Any)`
    :   Set state of stream with corresponding name

    `stream_has_state(self, name: str) ‑> bool`
    :   Tell if stream supports incremental sync