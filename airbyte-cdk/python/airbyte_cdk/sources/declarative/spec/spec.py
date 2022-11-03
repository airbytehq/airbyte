#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Mapping

from airbyte_cdk.models.airbyte_protocol import ConnectorSpecification
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class Spec(JsonSchemaMixin):
    """
    Returns a connection specification made up of information about the connector and how it can be configured

    Attributes:
        documentation_url (str): The link the Airbyte documentation about this connector
        connection_specification (Mapping[str, Any]): information related to how a connector can be configured
    """

    documentation_url: str
    connection_specification: Mapping[str, Any]
    options: InitVar[Mapping[str, Any]]

    def generate_spec(self) -> ConnectorSpecification:
        """
        Returns the connector specification according the spec block defined in the low code connector manifest.
        """

        # We remap these keys to camel case because that's the existing format expected by the rest of the platform
        return ConnectorSpecification.parse_obj(
            {"documentationUrl": self.documentation_url, "connectionSpecification": self.connection_specification}
        )
