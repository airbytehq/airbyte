Module airbyte_cdk.sources.deprecated.base_source
=================================================

Classes
-------

`BaseSource()`
:   Base source that designed to work with clients derived from BaseClient

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.source.Source
    * airbyte_cdk.connector.DefaultConnectorMixin
    * airbyte_cdk.sources.source.BaseSource
    * airbyte_cdk.connector.BaseConnector
    * abc.ABC
    * typing.Generic

    ### Class variables

    `client_class: Type[airbyte_cdk.sources.deprecated.client.BaseClient]`
    :

    ### Instance variables

    `name: str`
    :   Source name

    ### Methods

    `check(self, logger: logging.Logger, config: Mapping[str, Any]) ‑> airbyte_cdk.models.airbyte_protocol.AirbyteConnectionStatus`
    :   Check connection

    `discover(self, logger: logging.Logger, config: Mapping[str, Any]) ‑> airbyte_cdk.models.airbyte_protocol.AirbyteCatalog`
    :   Discover streams