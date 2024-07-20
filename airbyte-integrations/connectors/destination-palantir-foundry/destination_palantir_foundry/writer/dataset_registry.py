from destination_palantir_foundry.utils.resource_names import get_foundry_resource_name
from typing import Optional


class DatasetRegistry:
    def __init__(self) -> None:
        self._registry = {}

    def add(self, namespace: str, stream_name: str, dataset_rid: str):
        self._registry[get_foundry_resource_name(
            namespace, stream_name)] = dataset_rid

    def get(self, namespace: str, stream_name: str) -> Optional[str]:
        return self._registry.get(get_foundry_resource_name(namespace, stream_name), None)
