Module airbyte_cdk.sources
==========================

Sub-modules
-----------
* airbyte_cdk.sources.abstract_source
* airbyte_cdk.sources.config
* airbyte_cdk.sources.declarative
* airbyte_cdk.sources.deprecated
* airbyte_cdk.sources.singer
* airbyte_cdk.sources.source
* airbyte_cdk.sources.streams
* airbyte_cdk.sources.utils

Classes
-------

`AbstractSource()`
:   Abstract base class for an Airbyte Source. Consumers should implement any abstract methods
    in this class to create an Airbyte Specification compliant Source.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.source.Source
    * airbyte_cdk.connector.DefaultConnectorMixin
    * airbyte_cdk.sources.source.BaseSource
    * airbyte_cdk.connector.BaseConnector
    * abc.ABC
    * typing.Generic

    ### Descendants

    * airbyte_cdk.sources.declarative.declarative_source.DeclarativeSource

    ### Instance variables

    `name: str`
    :   Source name

    ### Methods

    `check(self, logger: logging.Logger, config: Mapping[str, Any]) ‑> airbyte_cdk.models.airbyte_protocol.AirbyteConnectionStatus`
    :   Implements the Check Connection operation from the Airbyte Specification.
        See https://docs.airbyte.io/architecture/airbyte-protocol.

    `check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) ‑> Tuple[bool, Optional[Any]]`
    :   :param logger: source logger
        :param config: The user-provided configuration as specified by the source's spec.
          This usually contains information required to check connection e.g. tokens, secrets and keys etc.
        :return: A tuple of (boolean, error). If boolean is true, then the connection check is successful
          and we can connect to the underlying data source using the provided configuration.
          Otherwise, the input config cannot be used to connect to the underlying data source,
          and the "error" object should describe what went wrong.
          The error object will be cast to string to display the problem to the user.

    `discover(self, logger: logging.Logger, config: Mapping[str, Any]) ‑> airbyte_cdk.models.airbyte_protocol.AirbyteCatalog`
    :   Implements the Discover operation from the Airbyte Specification.
        See https://docs.airbyte.io/architecture/airbyte-protocol.

    `read(self, logger: logging.Logger, config: Mapping[str, Any], catalog: airbyte_cdk.models.airbyte_protocol.ConfiguredAirbyteCatalog, state: MutableMapping[str, Any] = None) ‑> Iterator[airbyte_cdk.models.airbyte_protocol.AirbyteMessage]`
    :   Implements the Read operation from the Airbyte Specification. See https://docs.airbyte.io/architecture/airbyte-protocol.

    `streams(self, config: Mapping[str, Any]) ‑> List[airbyte_cdk.sources.streams.core.Stream]`
    :   :param config: The user-provided configuration as specified by the source's spec.
        Any stream construction related operation should happen here.
        :return: A list of the streams in this source connector.

`BaseConfig(**data: Any)`
:   Base class for connector spec, adds the following behaviour:
    
    - resolve $ref and replace it with definition
    - replace all occurrences of anyOf with oneOf
    - drop description
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Static methods

    `schema(*args, **kwargs) ‑> Dict[str, Any]`
    :   We're overriding the schema classmethod to enable some post-processing

`Source()`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * airbyte_cdk.connector.DefaultConnectorMixin
    * airbyte_cdk.sources.source.BaseSource
    * airbyte_cdk.connector.BaseConnector
    * abc.ABC
    * typing.Generic

    ### Descendants

    * airbyte_cdk.sources.abstract_source.AbstractSource
    * airbyte_cdk.sources.deprecated.base_source.BaseSource

    ### Class variables

    `check_config_against_spec: bool`
    :

    ### Methods

    `read_catalog(self, catalog_path: str) ‑> airbyte_cdk.models.airbyte_protocol.ConfiguredAirbyteCatalog`
    :

    `read_state(self, state_path: str) ‑> Dict[str, Any]`
    :