from destination_palantir_foundry.utils.resource_names import get_foundry_resource_name
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class BufferRegistryEntry:
    dataset_rid: str
    view_rid: str
    records: List[Dict]


class FoundryStreamBufferRegistry:
    def __init__(self) -> None:
        self._registry: Dict[str, BufferRegistryEntry] = {}

    def register_foundry_stream(self, namespace: str, stream_name: str, dataset_rid: str, view_rid: str):
        self._registry[get_foundry_resource_name(
            namespace, stream_name)] = BufferRegistryEntry(dataset_rid, view_rid, [])

    def add_record_to_buffer(self, namespace: str, stream_name: str, record: Dict[str, Any]):
        resource_name = get_foundry_resource_name(namespace, stream_name)

        entry = self._registry.get(
            resource_name, None)
        if entry is not None:
            entry.records.append(record)
        else:
            raise ValueError(
                f"Cannot add record to buffer for unregistered: {resource_name}"
            )

    def flush_buffer(self, namespace: str, stream_name: str) -> BufferRegistryEntry:
        resource_name = get_foundry_resource_name(namespace, stream_name)

        entry = self._registry.get(resource_name, None)
        if entry is not None:
            self._registry[resource_name] = BufferRegistryEntry(entry.dataset_rid, entry.view_rid, [])
            return entry
        else:
            raise ValueError(
                f"Cannot flush buffer for unregistered: {resource_name}")

    def get(self, namespace: str, stream_name: str) -> Optional[BufferRegistryEntry]:
        return self._registry.get(get_foundry_resource_name(namespace, stream_name), None)
