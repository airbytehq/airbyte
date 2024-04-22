#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.config_observation import emit_configuration_as_airbyte_control_message
from airbyte_cdk.sources.declarative.models import OAuthConfigSpecification
from airbyte_cdk.sources.file_based.file_based_source import FileBasedSource
from airbyte_protocol.models import AdvancedAuth, ConnectorSpecification

from .legacy_config_transformer import LegacyConfigTransformer


class SourceAzureBlobStorage(FileBasedSource):
    @classmethod
    def read_config(cls, config_path: str) -> Mapping[str, Any]:
        """
        Used to override the default read_config so that when the new file-based Azure Blob Storage connector processes a config
        in the legacy format, it can be transformed into the new config. This happens in entrypoint before we
        validate the config against the new spec.
        """
        config = FileBasedSource.read_config(config_path)
        if not cls._is_v1_config(config):
            converted_config = LegacyConfigTransformer.convert(config)
            emit_configuration_as_airbyte_control_message(converted_config)
            return converted_config
        return config

    @staticmethod
    def _is_v1_config(config: Mapping[str, Any]) -> bool:
        return "streams" in config

    def spec(self, *args: Any, **kwargs: Any) -> ConnectorSpecification:
        """
        Returns the specification describing what fields can be configured by a user when setting up a file-based source.
        """

        return ConnectorSpecification(
            documentationUrl=self.spec_class.documentation_url(),
            connectionSpecification=self.spec_class.schema(),
            advanced_auth=AdvancedAuth(
                auth_flow_type="oauth2.0",
                predicate_key=["credentials", "auth_type"],
                predicate_value="oauth2",
                oauth_config_specification=OAuthConfigSpecification(
                    complete_oauth_output_specification={
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {"refresh_token": {"type": "string", "path_in_connector_config": ["credentials", "refresh_token"]}},
                    },
                    complete_oauth_server_input_specification={
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {"client_id": {"type": "string"}, "client_secret": {"type": "string"}},
                    },
                    complete_oauth_server_output_specification={
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "client_id": {"type": "string", "path_in_connector_config": ["credentials", "client_id"]},
                            "client_secret": {"type": "string", "path_in_connector_config": ["credentials", "client_secret"]},
                        },
                    },
                    oauth_user_input_from_connector_config_specification={
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {"tenant_id": {"type": "string", "path_in_connector_config": ["credentials", "tenant_id"]}},
                    },
                ),
            ),
        )
