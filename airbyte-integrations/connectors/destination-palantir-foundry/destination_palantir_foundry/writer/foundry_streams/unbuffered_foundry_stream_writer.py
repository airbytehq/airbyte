from typing import Dict
from destination_palantir_foundry.writer.writer import Writer
from destination_palantir_foundry.foundry_api.stream_catalog import StreamCatalog
from destination_palantir_foundry.foundry_api.compass import Compass
from destination_palantir_foundry.utils.resource_names import get_foundry_resource_name
import logging

logger = logging.getLogger("airbyte")


class UnbufferedFoundryStreamWriter(Writer):
    def __init__(self, compass: Compass, stream_catalog: StreamCatalog, parent_rid: str) -> None:
        self.compass = compass
        self.stream_catalog = stream_catalog
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
                f"Existing Foundry stream was found for {resource_name}")
        else:
            logger.info(
                f"No existing Foundry stream found for stream {resource_name}, creating a new one.")
            self.stream_catalog.create_stream(self.parent_rid, resource_name)

    def add_row(self, namespace: str, stream_name: str, row: Dict):
        return super().add_row(namespace, stream_name, row)

    def ensure_flushed(self, namespace: str, stream_name: str):
        return super().ensure_flushed(namespace, stream_name)
