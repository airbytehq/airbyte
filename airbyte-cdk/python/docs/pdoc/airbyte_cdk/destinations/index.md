Module airbyte_cdk.destinations
===============================

Sub-modules
-----------
* airbyte_cdk.destinations.destination

Classes
-------

`Destination()`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * airbyte_cdk.connector.Connector
    * airbyte_cdk.connector.DefaultConnectorMixin
    * airbyte_cdk.connector.BaseConnector
    * abc.ABC
    * typing.Generic

    ### Class variables

    `VALID_CMDS`
    :

    `check_config_against_spec: bool`
    :

    ### Methods

    `parse_args(self, args: List[str]) ‑> argparse.Namespace`
    :   :param args: commandline arguments
        :return:

    `run(self, args: List[str])`
    :

    `run_cmd(self, parsed_args: argparse.Namespace) ‑> Iterable[airbyte_cdk.models.airbyte_protocol.AirbyteMessage]`
    :

    `write(self, config: Mapping[str, Any], configured_catalog: airbyte_cdk.models.airbyte_protocol.ConfiguredAirbyteCatalog, input_messages: Iterable[airbyte_cdk.models.airbyte_protocol.AirbyteMessage]) ‑> Iterable[airbyte_cdk.models.airbyte_protocol.AirbyteMessage]`
    :   Implement to define how the connector writes data to the destination