#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass, field
from typing import Any, List, Mapping, MutableMapping, Optional

from airbyte_cdk.models import (
    AdvancedAuth,
    ConnectorSpecification,
    ConnectorSpecificationSerializer,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import AuthFlow
from airbyte_cdk.sources.declarative.transformations.config_transformations.config_transformation import (
    ConfigTransformation,
)
from airbyte_cdk.sources.declarative.validators.validator import Validator
from airbyte_cdk.sources.message.repository import InMemoryMessageRepository, MessageRepository


@dataclass
class ConfigMigration:
    transformations: List[ConfigTransformation]
    description: Optional[str] = None


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
    config_migrations: List[ConfigMigration] = field(default_factory=list)
    config_transformations: List[ConfigTransformation] = field(default_factory=list)
    config_validations: List[Validator] = field(default_factory=list)

    def generate_spec(self) -> ConnectorSpecification:
        """
        Returns the connector specification according the spec block defined in the low code connector manifest.
        """

        obj: dict[str, Mapping[str, Any] | str | AdvancedAuth] = {
            "connectionSpecification": self.connection_specification
        }

        if self.documentation_url:
            obj["documentationUrl"] = self.documentation_url
        if self.advanced_auth:
            self.advanced_auth.auth_flow_type = self.advanced_auth.auth_flow_type.value  # type: ignore # We know this is always assigned to an AuthFlow which has the auth_flow_type field
            # Map CDK AuthFlow model to protocol AdvancedAuth model
            obj["advanced_auth"] = self.advanced_auth.dict()

        # We remap these keys to camel case because that's the existing format expected by the rest of the platform
        return ConnectorSpecificationSerializer.load(obj)

    def migrate_config(self, config: MutableMapping[str, Any]) -> None:
        """
        Apply all specified config transformations to the provided config and emit a control message.

        :param config: The user-provided config to migrate
        """
        for migration in self.config_migrations:
            for transformation in migration.transformations:
                transformation.transform(config)

    def transform_config(self, config: MutableMapping[str, Any]) -> None:
        """
        Apply all config transformations to the provided config.

        :param config: The user-provided configuration
        """
        for transformation in self.config_transformations:
            transformation.transform(config)

    def validate_config(self, config: Mapping[str, Any]) -> None:
        """
        Apply all config validations to the provided config.

        :param config: The user-provided configuration
        """
        for validator in self.config_validations:
            validator.validate(config)
