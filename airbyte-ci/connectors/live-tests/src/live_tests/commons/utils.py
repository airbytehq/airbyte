# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from typing import Dict, List, Optional

import dagger
from live_tests.commons.connector_runner import SecretDict, get_connector_container
from live_tests.commons.models import ConnectorUnderTest


def get_connector_config(path: Optional[str | Path]) -> Optional[SecretDict]:
    if path is None:
        return None
    return SecretDict(_read_json(path))


def get_state(path: Optional[str | Path]) -> Optional[Dict]:
    if path is None:
        return None
    return _read_json(path)


def _read_json(path: Path | str) -> Dict:
    with open(str(path), "r") as file:
        contents = file.read()
    return json.loads(contents)


async def get_connector_under_test(dagger_client: dagger.Client, connector_image_name: str) -> ConnectorUnderTest:
    dagger_container = await get_connector_container(dagger_client, connector_image_name)
    return ConnectorUnderTest(connector_image_name, dagger_container)


def sh_dash_c(lines: List[str]) -> List[str]:
    """Wrap sequence of commands in shell for safe usage of dagger Container's with_exec method."""
    return ["sh", "-c", " && ".join(["set -o xtrace"] + lines)]
