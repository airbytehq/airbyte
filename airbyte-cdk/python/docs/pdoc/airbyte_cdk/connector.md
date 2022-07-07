Module airbyte_cdk.connector
============================

Functions
---------

    
`load_optional_package_file(package: str, filename: str) ‑> Optional[bytes]`
:   Gets a resource from a package, returning None if it does not exist

Classes
-------

`AirbyteSpec(spec_string)`
:   

    ### Static methods

    `from_file(file_name: str)`
    :

`BaseConnector()`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * abc.ABC
    * typing.Generic

    ### Descendants

    * airbyte_cdk.connector.Connector
    * airbyte_cdk.sources.source.BaseSource

    ### Class variables

    `check_config_against_spec: bool`
    :

    ### Static methods

    `read_config(config_path: str) ‑> ~TConfig`
    :

    `write_config(config: ~TConfig, config_path: str)`
    :

    ### Methods

    `check(self, logger: logging.Logger, config: ~TConfig) ‑> airbyte_cdk.models.airbyte_protocol.AirbyteConnectionStatus`
    :   Tests if the input configuration can be used to successfully connect to the integration e.g: if a provided Stripe API token can be used to connect
        to the Stripe API.

    `configure(self, config: Mapping[str, Any], temp_dir: str) ‑> ~TConfig`
    :   Persist config in temporary directory to run the Source job

    `spec(self, logger: logging.Logger) ‑> airbyte_cdk.models.airbyte_protocol.ConnectorSpecification`
    :   Returns the spec for this integration. The spec is a JSON-Schema object describing the required configurations (e.g: username and password)
        required to run this integration. By default, this will be loaded from a "spec.yaml" or a "spec.json" in the package root.

`Connector()`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * airbyte_cdk.connector.DefaultConnectorMixin
    * airbyte_cdk.connector.BaseConnector
    * abc.ABC
    * typing.Generic

    ### Descendants

    * airbyte_cdk.destinations.destination.Destination

    ### Class variables

    `check_config_against_spec: bool`
    :

`DefaultConnectorMixin()`
:   

    ### Descendants

    * airbyte_cdk.connector.Connector
    * airbyte_cdk.sources.source.Source

    ### Methods

    `configure(self: airbyte_cdk.connector._WriteConfigProtocol, config: Mapping[str, Any], temp_dir: str) ‑> Mapping[str, Any]`
    :