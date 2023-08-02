#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Optional

from airbyte_cdk.models.airbyte_protocol import ConnectorSpecification
from airbyte_cdk.sources.declarative.models.declarative_component_schema import AuthFlow


@dataclass
class Spec:
    """
    Returns a connection specification made up of information about the connector and how it can be configured

    Attributes:
        connection_specification (Mapping[str, Any]): information related to how a connector can be configured
        documentation_url (Optional[str]): The link the Airbyte documentation about this connector
    """

    connection_specification: Mapping[str, Any]
    parameters: InitVar[Mapping[str, Any]]
    documentation_url: Optional[str] = None
    advanced_auth: Optional[AuthFlow] = None

    def generate_spec(self) -> ConnectorSpecification:
        """
        Returns the connector specification according the spec block defined in the low code connector manifest.
        """

        obj = {"connectionSpecification": self.connection_specification}

        if self.documentation_url:
            obj["documentationUrl"] = self.documentation_url
        if self.advanced_auth:
            obj["advanced_auth"] = self.advanced_auth
            obj["advanced_auth"].auth_flow_type = obj["advanced_auth"].auth_flow_type.value  # Get enum value

        # We remap these keys to camel case because that's the existing format expected by the rest of the platform
        return ConnectorSpecification.parse_obj(obj)
