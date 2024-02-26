import json
import os
from typing import Dict, Optional

from .connector_runner import SecretDict, get_connector_container


def get_connector_config(path: Optional[str]) -> Optional[SecretDict]:
    if path is None:
        return None
    return SecretDict(_read_json(path))


def get_state(path: Optional[str]) -> Optional[Dict]:
    if path is None:
        return None
    return _read_json(path)


def _read_json(path: str) -> Dict:
    with open(str(path), "r") as file:
        contents = file.read()
    return json.loads(contents)


async def get_connector(dagger_client, image_name):
    connector_container = await get_connector_container(dagger_client, image_name)
    if cachebuster := os.environ.get("CACHEBUSTER"):
        connector_container = connector_container.with_env_variable("CACHEBUSTER", cachebuster)
    return await connector_container
