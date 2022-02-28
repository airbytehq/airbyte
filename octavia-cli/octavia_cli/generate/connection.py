#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import yaml
from airbyte_api_client import api
from airbyte_api_client.model.airbyte_catalog import AirbyteCatalog
from airbyte_api_client.model.airbyte_stream import AirbyteStream
from airbyte_api_client.model.airbyte_stream_and_configuration import AirbyteStreamAndConfiguration
from airbyte_api_client.model.airbyte_stream_configuration import AirbyteStreamConfiguration
from airbyte_api_client.model.connection_create import ConnectionCreate
from airbyte_api_client.model.connection_schedule import ConnectionSchedule
from airbyte_api_client.model.connection_status import ConnectionStatus
from airbyte_api_client.model.destination_sync_mode import DestinationSyncMode
from airbyte_api_client.model.namespace_definition_type import NamespaceDefinitionType
from airbyte_api_client.model.resource_requirements import ResourceRequirements
from airbyte_api_client.model.source_id_request_body import SourceIdRequestBody
from airbyte_api_client.model.sync_mode import SyncMode
from yaml import Dumper


def dict_to_yaml(d):
    with open("/tmp/octavia-config/data.yml", "w+") as outfile:
        yaml.dump(d, outfile, Dumper=Dumper)


class Connection:
    def __init__(self, api_client, source_id, destination_id, resource_name):
        self.api_client = api_client
        self.source_api = api.source_api.SourceApi(api_client)
        self.connection_api = api.connection_api.ConnectionApi(api_client)
        self.source_id = source_id
        self.destination_id = destination_id
        self.resource_name = resource_name

    def get_source_catalog(self):
        source_id_request_body = SourceIdRequestBody(source_id=self.source_id)
        catalog = self.source_api.discover_schema_for_source(source_id_request_body, _check_return_type=False).catalog
        return catalog

    def generate(self) -> ConnectionCreate:
        catalog = self.get_source_catalog()
        connection_create = ConnectionCreate(
            name=self.resource_name,
            namespace_definition=NamespaceDefinitionType("source"),
            namespace_format="",
            prefix="",
            source_id=self.source_id,
            destination_id=self.destination_id,
            operation_ids=[
                "6c9e2330-4af3-47a9-b252-12fcfefcab55",
            ],
            sync_catalog=AirbyteCatalog(
                streams=[
                    AirbyteStreamAndConfiguration(
                        stream=AirbyteStream(
                            name=s.get("stream").get("name"),
                            json_schema={},
                            supported_sync_modes=[
                                SyncMode("full_refresh"),
                            ],
                            source_defined_cursor=False,
                            default_cursor_field=[],
                            source_defined_primary_key=[],
                            namespace="",
                        ),
                        config=AirbyteStreamConfiguration(
                            sync_mode=SyncMode("full_refresh"),
                            cursor_field=[],
                            destination_sync_mode=DestinationSyncMode("append"),
                            primary_key=[],
                            alias_name="alias_name_example",
                            selected=True,
                        ),
                    )
                    for s in catalog.get("streams")
                ],
            ),
            schedule=ConnectionSchedule(
                units=24,
                time_unit="hours",
            ),
            status=ConnectionStatus("active"),
            resource_requirements=ResourceRequirements(
                cpu_request="",
                cpu_limit="",
                memory_request="",
                memory_limit="",
            ),
        )

        # new_connection = self.connection_api.create_connection(connection_create)
        # this trigger the API to create a new connection
        # dict_to_yaml(connection_create.to_dict())

        return connection_create
