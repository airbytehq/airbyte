# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

import requests

from airbyte_lib.version import get_version


@dataclass
class ConnectorMetadata:
    name: str
    latest_available_version: str


_cache: dict[str, ConnectorMetadata] | None = None

REGISTRY_URL = "https://connectors.airbyte.com/files/registries/v0/oss_registry.json"


def _update_cache() -> None:
    global _cache
    if os.environ.get("AIRBYTE_LOCAL_REGISTRY"):
        with Path(str(os.environ.get("AIRBYTE_LOCAL_REGISTRY"))).open() as f:
            data = json.load(f)
    else:
        response = requests.get(
            REGISTRY_URL, headers={"User-Agent": f"airbyte-lib-{get_version()}"}
        )
        response.raise_for_status()
        data = response.json()
    _cache = {}
    for connector in data["sources"]:
        name = connector["dockerRepository"].replace("airbyte/", "")
        _cache[name] = ConnectorMetadata(name, connector["dockerImageTag"])


def get_connector_metadata(name: str) -> ConnectorMetadata:
    """Check the cache for the connector.

    If the cache is empty, populate by calling update_cache.
    """
    if not _cache:
        _update_cache()
    if not _cache or name not in _cache:
        raise Exception(f"Connector {name} not found")
    return _cache[name]
