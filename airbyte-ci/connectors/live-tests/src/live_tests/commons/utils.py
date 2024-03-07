# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import List

import dagger
from live_tests.commons.connector_runner import get_connector_container
from live_tests.commons.models import ConnectorUnderTest


async def get_connector_under_test(dagger_client: dagger.Client, connector_image_name: str) -> ConnectorUnderTest:
    dagger_container = await get_connector_container(dagger_client, connector_image_name)
    return ConnectorUnderTest(connector_image_name, dagger_container)


def sh_dash_c(lines: List[str]) -> List[str]:
    """Wrap sequence of commands in shell for safe usage of dagger Container's with_exec method."""
    return ["sh", "-c", " && ".join(["set -o xtrace"] + lines)]
