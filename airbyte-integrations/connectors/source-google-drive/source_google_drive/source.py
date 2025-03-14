#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, Mapping, Optional

from airbyte_cdk import AdvancedAuth, ConfiguredAirbyteCatalog, ConnectorSpecification, OAuthConfigSpecification, TState
from airbyte_cdk.models import AuthFlowType, OauthConnectorInputSpecification
from airbyte_cdk.sources.file_based.file_based_source import FileBasedSource
from airbyte_cdk.sources.file_based.stream.cursor.default_file_based_cursor import DefaultFileBasedCursor
from source_google_drive.spec import SourceGoogleDriveSpec
from source_google_drive.stream_reader import SourceGoogleDriveStreamReader


class SourceGoogleDrive(FileBasedSource):
    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: Optional[TState]):
        super().__init__(
            stream_reader=SourceGoogleDriveStreamReader(),
            spec_class=SourceGoogleDriveSpec,
            catalog=catalog,
            config=config,
            state=state,
            cursor_cls=DefaultFileBasedCursor,
        )

    def spec(self, *args: Any, **kwargs: Any) -> ConnectorSpecification:
        """
        Returns the specification describing what fields can be configured by a user when setting up a file-based source.
        """
        oauth_connector_input_specification = OauthConnectorInputSpecification(
            consent_url="https://accounts.google.com/o/oauth2/v2/auth?{{client_id_param}}&{{redirect_uri_param}}&response_type=code&{{scope_param}}&access_type=offline&{{state_param}}&include_granted_scopes=true&prompt=consent",
            access_token_url="https://oauth2.googleapis.com/token?{{client_id_param}}&{{client_secret_param}}&{{auth_code_param}}&{{redirect_uri_param}}&grant_type=authorization_code",
            scope="https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/admin.directory.group.readonly https://www.googleapis.com/auth/admin.directory.group.member.readonly https://www.googleapis.com/auth/admin.directory.user.readonly",
        )

        return ConnectorSpecification(
            documentationUrl=self.spec_class.documentation_url(),
            connectionSpecification=self.spec_class.schema(),
            advanced_auth=AdvancedAuth(
                auth_flow_type=AuthFlowType.oauth2_0,
                predicate_key=["credentials", "auth_type"],
                predicate_value="Client",
                oauth_config_specification=OAuthConfigSpecification(
                    oauth_connector_input_specification=oauth_connector_input_specification,
                    complete_oauth_output_specification={
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "refresh_token": {
                                "type": "string",
                                "path_in_connector_config": ["credentials", "refresh_token"],
                                "path_in_oauth_response": ["refresh_token"],
                            }
                        },
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
                ),
            ),
        )
