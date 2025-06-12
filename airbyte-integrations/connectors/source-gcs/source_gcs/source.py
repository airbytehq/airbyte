#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, Mapping, Optional

from airbyte_cdk import emit_configuration_as_airbyte_control_message
from airbyte_cdk.models import AdvancedAuth, AuthFlowType, ConnectorSpecification, OAuthConfigSpecification
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.file_based_source import FileBasedSource
from airbyte_cdk.sources.file_based.stream import AbstractFileBasedStream
from airbyte_cdk.sources.file_based.stream.cursor import AbstractFileBasedCursor
from source_gcs.legacy_config_transformer import LegacyConfigTransformer
from source_gcs.spec import SourceGCSSpec
from source_gcs.stream import GCSStream


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
                auth_flow_type=AuthFlowType.oauth2_0,
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

    def _make_default_stream(
        self, stream_config: FileBasedStreamConfig, cursor: Optional[AbstractFileBasedCursor]
    ) -> AbstractFileBasedStream:
        return GCSStream(
            config=stream_config,
            catalog_schema=self.stream_schemas.get(stream_config.name),
            stream_reader=self.stream_reader,
            availability_strategy=self.availability_strategy,
            discovery_policy=self.discovery_policy,
            parsers=self.parsers,
            validation_policy=self._validate_and_get_validation_policy(stream_config),
            errors_collector=self.errors_collector,
            cursor=cursor,
        )
