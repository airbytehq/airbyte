import asyncio
import logging
import sys
from enum import Enum
from typing import Dict, Optional

import dagger
from airbyte_protocol.models import ConfiguredAirbyteCatalog

from live_tests.utils.connector_runner import ConnectorRunner, SecretDict
from live_tests.backends import BaseBackend, FileBackend
from live_tests.regression_tests.comparators import DiffComparator
from live_tests.utils.common import ConnectorUnderTest, get_connector

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

COMMANDS = ["check", "discover", "read", "read-with-state", "spec"]


class Command(Enum):
    CHECK = "check"
    DISCOVER = "discover"
    READ = "read"
    READ_WITH_STATE = "read-with-state"
    SPEC = "spec"


async def run(
    connector_name: str,
    control_image_name: str,
    target_image_name: str,
    output_directory: str,
    command: str,
    config: Optional[SecretDict],
    catalog: Optional[ConfiguredAirbyteCatalog],
    state: Optional[Dict],
):
    async with (dagger.Connection(config=dagger.Config(log_output=sys.stderr)) as client):
        control_connector = await get_connector(client, connector_name, control_image_name)
        target_connector = await get_connector(client, connector_name, target_image_name)
        await _run(
            control_connector, target_connector, output_directory, command, config, catalog, state
        )
        await DiffComparator(client, output_directory).compare(control_connector, target_connector)


async def _run(
    control_connector: ConnectorUnderTest,
    target_connector: ConnectorUnderTest,
    output_directory: str,
    command: str,
    config: Optional[SecretDict],
    catalog: Optional[ConfiguredAirbyteCatalog],
    state: Optional[Dict],
):
    # TODO: maybe use proxy to cache the response from the first round and use the cache for the second round
    #   (this may only make sense for syncs with an input state)
    if command == "all":
        tasks = []
        for _command in COMMANDS:
            tasks.extend([
                _dispatch(
                    connector.container,
                    FileBackend(f"{output_directory}/{connector.version}/{_command}"),
                    f"{output_directory}/{connector.version}",
                    _command,
                    config,
                    catalog,
                    state,
                ) for connector in [control_connector, target_connector]
            ])
    else:
        tasks = [
            _dispatch(
                connector.container,
                FileBackend(f"{output_directory}/{connector.version}/{command}"),
                f"{output_directory}/{connector.version}",
                command,
                config,
                catalog,
                state,
            ) for connector in [control_connector, target_connector]
        ]
    await asyncio.gather(*tasks)


async def _dispatch(
    container: dagger.Container,
    backend: BaseBackend,
    output_directory: str,
    command: str,
    config: Optional[SecretDict],
    catalog: Optional[ConfiguredAirbyteCatalog],
    state: Optional[Dict],
):
    runner = ConnectorRunner(container, backend, f"{output_directory}/{command}")

    if command == "check":
        await runner.call_check(config)

    elif command == "discover":
        await runner.call_discover(config)

    elif command == "read":
        await runner.call_read(config, catalog)

    elif command == "read-with-state":
        await runner.call_read_with_state(config, catalog, state)

    elif command == "spec":
        await runner.call_spec()

    else:
        raise NotImplementedError(f"{command} is not recognized. Must be one of {', '.join(COMMANDS)}")
