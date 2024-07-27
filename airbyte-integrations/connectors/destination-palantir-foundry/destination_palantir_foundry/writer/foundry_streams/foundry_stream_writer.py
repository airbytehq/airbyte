import logging
from sys import getsizeof

from airbyte_cdk.models.airbyte_protocol import ConfiguredAirbyteStream, AirbyteRecordMessage

from destination_palantir_foundry.foundry_api.foundry_metadata import FoundryMetadata
from destination_palantir_foundry.foundry_api.stream_catalog import StreamCatalog
from destination_palantir_foundry.foundry_api.stream_proxy import StreamProxy
from destination_palantir_foundry.foundry_schema.providers.streams.stream_schema_provider import StreamSchemaProvider
from destination_palantir_foundry.utils.project_helper import ProjectHelper
from destination_palantir_foundry.utils.resource_names import get_foundry_resource_name
from destination_palantir_foundry.writer.foundry_streams.foundry_stream_buffer_registry import \
    FoundryStreamBufferRegistry
from destination_palantir_foundry.writer.writer import Writer

logger = logging.getLogger("airbyte")


class FoundryStreamWriter(Writer):
    SCOPES = [  # TODO(jcrowson): find better scoping strategy
        "streaming:read",
        "streaming:create",
        "streaming:delete",
        "streaming:manage-resource",
        "streaming:write",
        "streaming:read-resource",
        "streaming:read",
        "streaming:create",
        "streaming:delete",
        "streaming:manage-resource",
        "streaming:write",
        "streaming:read-resource",
        "api:datasets-write",
        "api:datasets-read",
        "compass:read-branch",
        "compass:discover",
        "compass:view",
        "compass:read-resource",
        "compass:delete",
    ]

    def __init__(
            self,
            project_helper: ProjectHelper,
            stream_catalog: StreamCatalog,
            stream_proxy: StreamProxy,
            foundry_metadata: FoundryMetadata,
            buffer_registry: FoundryStreamBufferRegistry,
            stream_schema_provider: StreamSchemaProvider,
            parent_rid: str
    ) -> None:
        self.project_helper = project_helper
        self.stream_catalog = stream_catalog
        self.stream_proxy = stream_proxy
        self.foundry_metadata = foundry_metadata
        self.buffer_registry = buffer_registry
        self.stream_schema_provider = stream_schema_provider
        self.parent_rid = parent_rid

    def ensure_registered(self, airbyte_stream: ConfiguredAirbyteStream) -> None:
        namespace, stream_name = airbyte_stream.stream.namespace, airbyte_stream.stream.name
        resource_name = get_foundry_resource_name(namespace, stream_name)

        maybe_resource = self.project_helper.maybe_get_resource_by_name(self.parent_rid, resource_name)

        foundry_stream_schema = self.stream_schema_provider.get_foundry_stream_schema(
            airbyte_stream.stream)

        if maybe_resource is not None:
            maybe_stream = self.stream_catalog.get_stream(maybe_resource.rid).root
            if maybe_stream is None:
                raise ValueError(
                    f"Foundry resource '{resource_name}' ({maybe_resource.rid}) was found but it is not a stream.")

            logger.info(
                f"Existing Foundry stream was found for {resource_name}. Adding to registry.")
            self.buffer_registry.register_foundry_stream(
                namespace, stream_name, maybe_resource.rid, maybe_stream.view.viewRid, foundry_stream_schema)
        else:
            logger.info(
                f"No existing Foundry stream found for stream {resource_name}, creating a new one.")

            create_stream_response = self.stream_catalog.create_stream(
                self.parent_rid, resource_name)

            foundry_stream_dataset_rid = create_stream_response.view.datasetRid
            foundry_stream_view_rid = create_stream_response.view.viewRid

            self.buffer_registry.register_foundry_stream(
                namespace, stream_name, foundry_stream_dataset_rid, foundry_stream_view_rid, foundry_stream_schema)

            logger.info(
                f"Setting the new Foundry stream's schema.")
            self.foundry_metadata.put_schema(
                foundry_stream_dataset_rid, foundry_stream_schema)

    def add_record(self, airbyte_record: AirbyteRecordMessage, ):
        namespace, stream_name = airbyte_record.namespace, airbyte_record.stream

        registered_buffer = self.buffer_registry.get(namespace, stream_name)
        if registered_buffer is None:
            raise ValueError(
                f"Tried to add row to an unregistered stream for '{get_foundry_resource_name(airbyte_record.namespace, airbyte_record.stream)}'")

        self.buffer_registry.add_record_to_buffer(airbyte_record)

    def flush_to_destination(self, namespace: str, stream_name: str):
        buffer_entry = self.buffer_registry.flush_buffer(namespace, stream_name)
        if len(buffer_entry.records) == 0:
            return

        logger.info(
            f"Pushing {len(buffer_entry.records)} records to Foundry stream [rid: {buffer_entry.dataset_rid}, viewRid: {buffer_entry.view_rid}] - {getsizeof(buffer_entry.records)} bytes")

        converted_records = [
            self.stream_schema_provider.get_converted_record(
                record, buffer_entry.foundry_schema,
            ) for record in buffer_entry.records
        ]

        self.stream_proxy.put_json_records(
            buffer_entry.dataset_rid, buffer_entry.view_rid, converted_records
        )
