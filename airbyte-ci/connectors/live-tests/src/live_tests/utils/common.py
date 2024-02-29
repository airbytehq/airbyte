import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

import dagger

from live_tests.utils.connector_runner import SecretDict, get_connector_container


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


@dataclass
class ConnectorUnderTest:
    technical_name: str
    version: str
    container: dagger.Container


async def get_connector(dagger_client, connector_name: str, image_name: str) -> ConnectorUnderTest:
    dagger_container = await get_connector_container(dagger_client, image_name)
    if cachebuster := os.environ.get("CACHEBUSTER"):
        dagger_container = dagger_container.with_env_variable("CACHEBUSTER", cachebuster)

    return ConnectorUnderTest(connector_name, image_name.split(":")[-1], await dagger_container)


def sh_dash_c(lines: List[str]) -> List[str]:
    """Wrap sequence of commands in shell for safe usage of dagger Container's with_exec method."""
    return ["sh", "-c", " && ".join(["set -o xtrace"] + lines)]
