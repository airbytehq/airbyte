#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys
import traceback
from datetime import datetime
from typing import Any, List

from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from airbyte_cdk.models import (
    AdvancedAuth,
    AirbyteErrorTraceMessage,
    AirbyteMessage,
    AirbyteTraceMessage,
    ConnectorSpecification,
    OAuthConfigSpecification,
    TraceType,
    Type,
)
from airbyte_cdk.sources.file_based.file_based_source import FileBasedSource
from airbyte_cdk.sources.file_based.stream.cursor.default_file_based_cursor import DefaultFileBasedCursor
from source_google_drive.spec import SourceGoogleDriveSpec as Config
from source_google_drive.stream_reader import SourceGoogleDriveStreamReader


class GoogleDriveSource(FileBasedSource):
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
                predicate_value="Client",
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
                ),
            ),
        )


def get_source(args: List[str]):
    catalog_path = AirbyteEntrypoint.extract_catalog(args)
    try:
        return GoogleDriveSource(SourceGoogleDriveStreamReader(), Config, catalog_path, cursor_cls=DefaultFileBasedCursor)
    except Exception:
        print(
            AirbyteMessage(
                type=Type.TRACE,
                trace=AirbyteTraceMessage(
                    type=TraceType.ERROR,
                    emitted_at=int(datetime.now().timestamp() * 1000),
                    error=AirbyteErrorTraceMessage(
                        message="Error starting the sync. This could be due to an invalid configuration or catalog. Please contact Support for assistance.",
                        stack_trace=traceback.format_exc(),
                    ),
                ),
            ).json()
        )
        return None


if __name__ == "__main__":
    _args = sys.argv[1:]
    source = get_source(_args)

    if source:
        launch(source, _args)
