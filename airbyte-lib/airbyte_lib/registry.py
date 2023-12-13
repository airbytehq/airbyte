import requests
from dataclasses import dataclass

_cache = None

REGISTRY_URL = "https://connectors.airbyte.com/files/registries/v0/oss_registry.json"

@dataclass
class ConnectorMetadata:
    name: str
    version: str


def _update_cache():
    global _cache
    print("Updating cache")
    response = requests.get(REGISTRY_URL)
    response.raise_for_status()
    data = response.json()
    _cache = {}
    for connector in data["sources"]:
        name = connector["dockerRepository"].replace("airbyte/", "")
        _cache[name] = ConnectorMetadata(name, connector["dockerImageTag"])

def get_connector_metadata(name: str):
    """
    check the cache for the connector. If the cache is empty, populate by calling update_cache
    """
    if not _cache:
        _update_cache()
    return _cache[name]