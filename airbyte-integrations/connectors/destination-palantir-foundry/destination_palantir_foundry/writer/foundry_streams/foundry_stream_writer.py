from destination_palantir_foundry.writer.writer import Writer
from destination_palantir_foundry.foundry_api.stream_catalog import StreamCatalog
from destination_palantir_foundry.foundry_api.compass import Compass
from destination_palantir_foundry.foundry_api.stream_proxy import StreamProxy
from destination_palantir_foundry.foundry_api.foundry_metadata import FoundryMetadata
from destination_palantir_foundry.utils.resource_names import get_foundry_resource_name
from destination_palantir_foundry.writer.foundry_streams.foundry_stream_buffer_registry import FoundryStreamBufferRegistry
from destination_palantir_foundry.foundry_schema.providers.stream_schema_provider import StreamSchemaProvider
import logging
from airbyte_cdk.models.airbyte_protocol import ConfiguredAirbyteStream, AirbyteRecordMessage

logger = logging.getLogger("airbyte")


class FoundryStreamWriter(Writer):
    SCOPES = [  # TODO(jcrowson): scope down...
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
    ]

    def __init__(
            self,
            compass: Compass,
            stream_catalog: StreamCatalog,
            stream_proxy: StreamProxy,
            foundry_metadata: FoundryMetadata,
            buffer_registry: FoundryStreamBufferRegistry,
            stream_schema_provider: StreamSchemaProvider,
            parent_rid: str
    ) -> None:
        self.compass = compass
        self.stream_catalog = stream_catalog
        self.stream_proxy = stream_proxy
        self.foundry_metadata = foundry_metadata
        self.buffer_registry = buffer_registry
        self.stream_schema_provider = stream_schema_provider
        self.parent_rid = parent_rid

    def ensure_registered(self, airbyte_stream: ConfiguredAirbyteStream) -> None:
        rids_to_paths = self.compass.get_paths([self.parent_rid])
        parent_path = rids_to_paths.get(self.parent_rid)
        if parent_path is None:
            raise ValueError(
                f"Could not resolve path for parent {self.parent_rid}. Please ensure the project exists and that the client has access to it.")

        namespace, stream_name = airbyte_stream.stream.namespace, airbyte_stream.stream.name
        resource_name = get_foundry_resource_name(namespace, stream_name)

        maybe_resource = self.compass.get_resource_by_path(
            f"{parent_path}/{resource_name}")
        if maybe_resource is not None:
            maybe_stream = self.stream_catalog.get_stream(maybe_resource.rid)
            if maybe_stream is None:
                raise ValueError(
                    f"Foundry resource '{resource_name}' ({maybe_resource.rid}) was found but it is not a stream.")

            logger.info(
                f"Existing Foundry stream was found for {resource_name}. Adding to registry.")
            self.buffer_registry.register_foundry_stream(
                namespace, stream_name, maybe_resource.rid, maybe_stream.view.viewRid)
        else:
            logger.info(
                f"No existing Foundry stream found for stream {resource_name}, creating a new one.")

            create_stream_response = self.stream_catalog.create_stream(
                self.parent_rid, resource_name)

            foundry_stream_dataset_rid = create_stream_response.view.datasetRid
            foundry_stream_view_rid = create_stream_response.view.viewRid

            self.buffer_registry.register_foundry_stream(
                namespace, stream_name, foundry_stream_dataset_rid, foundry_stream_view_rid)

            logger.info(
                f"Setting the new Foundry stream's schema.")
            foundry_stream_schema = self.stream_schema_provider.get_foundry_stream_schema(
                airbyte_stream.stream)
            self.foundry_metadata.put_schema(
                foundry_stream_dataset_rid, foundry_stream_schema)

    def add_record(self, airbyte_record: AirbyteRecordMessage):
        namespace, stream_name = airbyte_record.namespace, airbyte_record.stream

        registered_buffer = self.buffer_registry.get(namespace, stream_name)
        if registered_buffer is None:
            raise ValueError(
                f"Tried to add row to an unregistered stream for '{get_foundry_resource_name(airbyte_record.namespace, airbyte_record.stream)}'")

        self.buffer_registry.add_record_to_buffer(namespace, stream_name, self.stream_schema_provider.get_converted_record(airbyte_record))

    def ensure_flushed(self, namespace: str, stream_name: str):
        buffer_entry = self.buffer_registry.flush_buffer(namespace, stream_name)
        if len(buffer_entry.records) == 0:
            return

        self.stream_proxy.put_json_records(buffer_entry.dataset_rid, buffer_entry.view_rid, buffer_entry.records)
