Module airbyte_cdk
==================

Sub-modules
-----------
* airbyte_cdk.connector
* airbyte_cdk.destinations
* airbyte_cdk.entrypoint
* airbyte_cdk.exception_handler
* airbyte_cdk.logger
* airbyte_cdk.models
* airbyte_cdk.sources
* airbyte_cdk.utils

Classes
-------

`AirbyteEntrypoint(source: airbyte_cdk.sources.source.Source)`
:   

    ### Static methods

    `parse_args(args: List[str]) ‑> argparse.Namespace`
    :

    ### Methods

    `run(self, parsed_args: argparse.Namespace) ‑> Iterable[str]`
    :

`AirbyteLogger(*args, **kwargs)`
:   

    ### Methods

    `debug(self, message)`
    :

    `error(self, message)`
    :

    `exception(self, message)`
    :

    `fatal(self, message)`
    :

    `info(self, message)`
    :

    `log(self, level, message)`
    :

    `trace(self, message)`
    :

    `warn(self, message)`
    :

`AirbyteSpec(spec_string)`
:   

    ### Static methods

    `from_file(file_name: str)`
    :

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