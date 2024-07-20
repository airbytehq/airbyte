from typing import Dict
from destination_palantir_foundry.writer.writer import Writer
from destination_palantir_foundry.foundry_api.stream_catalog import StreamCatalog
from destination_palantir_foundry.foundry_api.compass import Compass
from destination_palantir_foundry.foundry_api.stream_proxy import StreamProxy
from destination_palantir_foundry.utils.resource_names import get_foundry_resource_name
from destination_palantir_foundry.writer.dataset_registry import DatasetRegistry
import logging

logger = logging.getLogger("airbyte")


class UnbufferedFoundryStreamWriter(Writer):
    def __init__(self, compass: Compass, stream_catalog: StreamCatalog, stream_proxy: StreamProxy, dataset_registry: DatasetRegistry, parent_rid: str) -> None:
        self.compass = compass
        self.stream_catalog = stream_catalog
        self.stream_proxy = stream_proxy
        self.dataset_registry = dataset_registry
        self.parent_rid = parent_rid

    def ensure_registered(self, namespace: str, stream_name) -> None:
        rids_to_paths = self.compass.get_paths([self.parent_rid])
        parent_path = rids_to_paths.get(self.parent_rid)
        if parent_path is None:
            raise ValueError(
                f"Could not resolve path for parent {self.parent_rid}. Please ensure the project exists and that the client has access to it.")

        resource_name = get_foundry_resource_name(namespace, stream_name)

        maybe_resource = self.compass.get_resource_by_path(
            f"{parent_path}/{resource_name}")
        if maybe_resource is not None:
            logger.info(
                f"Existing Foundry stream was found for {resource_name}. Adding to registry.")
            self.dataset_registry.add(
                namespace, stream_name, maybe_resource.rid)
        else:
            logger.info(
                f"No existing Foundry stream found for stream {resource_name}, creating a new one.")
            create_stream_response = self.stream_catalog.create_stream(
                self.parent_rid, resource_name)
            self.dataset_registry.add(namespace, stream_name,
                                      create_stream_response.view.datasetRid)

    def add_record(self, namespace: str, stream_name: str, record: Dict):
        stream_dataset_rid = self.dataset_registry.get(namespace, stream_name)
        if stream_dataset_rid is None:
            raise ValueError(
                f"Tried to add row to an unregistered stream for '{get_foundry_resource_name(namespace, stream_name)}'")

        self.stream_proxy.put_json_record(stream_dataset_rid, record)

    def ensure_flushed(self, _namespace: str, _stream_name: str):
        # No buffering, so always flushed
        return
