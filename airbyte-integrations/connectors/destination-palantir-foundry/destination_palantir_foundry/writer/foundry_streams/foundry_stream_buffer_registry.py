from dataclasses import dataclass
from typing import Optional, List, Dict

from airbyte_protocol.models import AirbyteRecordMessage

from destination_palantir_foundry.foundry_schema.foundry_schema import FoundrySchema
from destination_palantir_foundry.utils.resource_names import get_foundry_resource_name


@dataclass
class BufferRegistryEntry:
    dataset_rid: str
    view_rid: str
    records: List[AirbyteRecordMessage]
    foundry_schema: FoundrySchema


class FoundryStreamBufferRegistry:
    def __init__(self) -> None:
        self._registry: Dict[str, BufferRegistryEntry] = {}

    def register_foundry_stream(self, namespace: Optional[str], stream_name: str, dataset_rid: str, view_rid: str,
                                foundry_schema: FoundrySchema):
        self._registry[get_foundry_resource_name(
            namespace, stream_name)] = BufferRegistryEntry(dataset_rid, view_rid, [], foundry_schema)

    def add_record_to_buffer(self, record: AirbyteRecordMessage):
        resource_name = get_foundry_resource_name(record.namespace, record.stream)

        entry = self._registry.get(
            resource_name, None)
        if entry is not None:
            entry.records.append(record)
        else:
            raise ValueError(
                f"Cannot add record to buffer for unregistered: {resource_name}"
            )

    def flush_buffer(self, namespace: Optional[str], stream_name: str) -> BufferRegistryEntry:
        resource_name = get_foundry_resource_name(namespace, stream_name)

        entry = self._registry.get(resource_name, None)
        if entry is not None:
            self._registry[resource_name] = BufferRegistryEntry(entry.dataset_rid, entry.view_rid, [], entry.foundry_schema)
            return entry
        else:
            raise ValueError(
                f"Cannot flush buffer for unregistered: {resource_name}")

    def get(self, namespace: Optional[str], stream_name: str) -> Optional[BufferRegistryEntry]:
        return self._registry.get(get_foundry_resource_name(namespace, stream_name), None)
