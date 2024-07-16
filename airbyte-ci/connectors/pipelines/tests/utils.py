#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import random
from unittest.mock import AsyncMock

from connector_ops.utils import Connector, ConnectorLanguage, get_all_connectors_in_repo

ALL_CONNECTORS = get_all_connectors_in_repo()


class MockContainerClass:
    """HACK: We Mock the Dagger.container class manually as AsyncMock does not properly infer the return type of the with_label and with_exec methods."""

    def with_label(self, *args, **kwargs):
        return self

    async def with_exec(self, *args, **kwargs):
        return self


def pick_a_random_connector(
    language: ConnectorLanguage = None, support_level: str = None, other_picked_connectors: list = None
) -> Connector:
    """Pick a random connector from the list of all connectors."""
    all_connectors = [c for c in list(ALL_CONNECTORS)]
    if language:
        all_connectors = [c for c in all_connectors if c.language is language]
    if support_level:
        all_connectors = [c for c in all_connectors if c.support_level == support_level]
    picked_connector = random.choice(all_connectors)
    if other_picked_connectors:
        while picked_connector in other_picked_connectors:
            picked_connector = random.choice(all_connectors)
    return picked_connector


def mock_container():
    container_mock = AsyncMock(MockContainerClass)
    container_mock.with_label.return_value = container_mock
    container_mock.with_exec.return_value = container_mock
    return container_mock
