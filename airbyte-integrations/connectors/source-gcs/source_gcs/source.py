#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, Mapping

from airbyte_cdk import emit_configuration_as_airbyte_control_message
from airbyte_cdk.models import AdvancedAuth, OAuthConfigSpecification
from airbyte_cdk.sources.file_based.file_based_source import FileBasedSource
from airbyte_protocol.models import ConnectorSpecification
from source_gcs.legacy_config_transformer import LegacyConfigTransformer
from source_gcs.spec import SourceGCSSpec


class SourceGCS(FileBasedSource):
    @classmethod
    def read_config(cls, config_path: str) -> Mapping[str, Any]:
        """
        Override the default read_config to transform the legacy config format
        into the new one before validating it against the new spec.
        """
        config = FileBasedSource.read_config(config_path)
        if not cls._is_file_based_config(config):
            parsed_legacy_config = SourceGCSSpec(**config)
            converted_config = LegacyConfigTransformer.convert(parsed_legacy_config)
            emit_configuration_as_airbyte_control_message(converted_config)
            return converted_config
        return config

    @staticmethod
    def _is_file_based_config(config: Mapping[str, Any]) -> bool:
        return "streams" in config

    def spec(self, *args: Any, **kwargs: Any) -> ConnectorSpecification:
        return ConnectorSpecification(
            documentationUrl=self.spec_class.documentation_url(),
            connectionSpecification=self.spec_class.schema(),
            advanced_auth=AdvancedAuth(
                auth_flow_type="oauth2.0",
                predicate_key=["credentials", "auth_type"],
                predicate_value="Client",
                oauth_config_specification=OAuthConfigSpecification(
                    complete_oauth_output_specification={
                        "type": "object",
                        "properties": {
                            "access_token": {"type": "string", "path_in_connector_config": ["credentials", "access_token"]},
                            "refresh_token": {"type": "string", "path_in_connector_config": ["credentials", "refresh_token"]},
                        },
                    },
                    complete_oauth_server_input_specification={
                        "type": "object",
                        "properties": {"client_id": {"type": "string"}, "client_secret": {"type": "string"}},
                    },
                    complete_oauth_server_output_specification={
                        "type": "object",
                        "properties": {
                            "client_id": {"type": "string", "path_in_connector_config": ["credentials", "client_id"]},
                            "client_secret": {"type": "string", "path_in_connector_config": ["credentials", "client_secret"]},
                        },
                    },
                ),
            ),
        )
