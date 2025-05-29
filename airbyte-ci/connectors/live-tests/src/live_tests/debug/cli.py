# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import logging
import textwrap
from pathlib import Path
from typing import Optional

import asyncclick as click
import dagger
from live_tests.commons.connection_objects_retrieval import COMMAND_TO_REQUIRED_OBJECT_TYPES, get_connection_objects
from live_tests.commons.connector_runner import ConnectorRunner
from live_tests.commons.models import ActorType, Command, ConnectionObjects, ConnectorUnderTest, ExecutionInputs, TargetOrControl
from live_tests.commons.utils import clean_up_artifacts
from live_tests.debug import DAGGER_CONFIG
from rich.prompt import Prompt

from .consts import MAIN_OUTPUT_DIRECTORY

LOGGER = logging.getLogger("debug_command")


@click.command(
    "debug",
    help="Run a specific command on one or multiple connectors and persists the outputs to local storage.",
)
@click.argument(
    "command",
    type=click.Choice([c.value for c in Command]),
    callback=lambda _, __, value: Command(value),
)
@click.option("--connection-id", type=str, required=False, default=None)
@click.option(
    "--config-path",
    type=click.Path(file_okay=True, readable=True, dir_okay=False, resolve_path=True, path_type=Path),
    required=False,
    default=None,
)
@click.option(
    "--catalog-path",
    type=click.Path(file_okay=True, readable=True, dir_okay=False, resolve_path=True, path_type=Path),
    required=False,
    default=None,
)
@click.option(
    "--state-path",
    type=click.Path(file_okay=True, readable=True, dir_okay=False, resolve_path=True, path_type=Path),
    required=False,
    default=None,
)
@click.option(
    "-c",
    "--connector-image",
    "connector_images",
    help="Docker image name of the connector to debug (e.g. `airbyte/source-faker:latest`, `airbyte/source-faker:dev`)",
    multiple=True,
    type=str,
    required=True,
)
# TODO add an env var options to pass to the connector
@click.pass_context
async def debug_cmd(
    ctx: click.Context,
    command: Command,
    connection_id: Optional[str],
    config_path: Optional[Path],
    catalog_path: Optional[Path],
    state_path: Optional[Path],
    connector_images: list[str],
) -> None:
    if connection_id:
        retrieval_reason = click.prompt("👮‍♂️ Please provide a reason for accessing the connection objects. This will be logged")
    else:
        retrieval_reason = None

    try:
        connection_objects = get_connection_objects(
            COMMAND_TO_REQUIRED_OBJECT_TYPES[command],
            connection_id,
            config_path,
            catalog_path,
            state_path,
            retrieval_reason,
        )
    except ValueError as e:
        raise click.UsageError(str(e))
    async with dagger.Connection(config=DAGGER_CONFIG) as dagger_client:
        MAIN_OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
        try:
            for connector_image in connector_images:
                await _execute_command_and_save_artifacts(
                    dagger_client,
                    connector_image,
                    command,
                    connection_objects,
                )

            Prompt.ask(
                textwrap.dedent(
                    """
                Debug artifacts will be destroyed after this prompt. 
                Press enter when you're done reading them.
                🚨 Do not copy them elsewhere on your disk!!! 🚨
                """
                )
            )
        finally:
            clean_up_artifacts(MAIN_OUTPUT_DIRECTORY, LOGGER)


async def _execute_command_and_save_artifacts(
    dagger_client: dagger.Client,
    connector_image: str,
    command: Command,
    connection_objects: ConnectionObjects,
) -> None:
    try:
        connector_under_test = await ConnectorUnderTest.from_image_name(dagger_client, connector_image, TargetOrControl.CONTROL)
        if connector_under_test.actor_type is ActorType.SOURCE:
            actor_id = connection_objects.source_id
        else:
            actor_id = connection_objects.destination_id
        assert actor_id is not None
        execution_inputs = ExecutionInputs(
            global_output_dir=MAIN_OUTPUT_DIRECTORY,
            connector_under_test=connector_under_test,
            command=command,
            config=connection_objects.source_config,
            configured_catalog=connection_objects.configured_catalog,
            state=connection_objects.state,
            environment_variables=None,
            actor_id=actor_id,
        )
    except ValueError as e:
        raise click.UsageError(str(e))
    execution_result = await ConnectorRunner(dagger_client, execution_inputs).run()
    await execution_result.save_artifacts(MAIN_OUTPUT_DIRECTORY)
