# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import time
from pathlib import Path
from typing import List, Optional

import asyncclick as click
import dagger
from live_tests.commons.connection_objects_retrieval import COMMAND_TO_REQUIRED_OBJECT_TYPES, get_connection_objects
from live_tests.commons.connector_runner import ConnectorRunner
from live_tests.commons.models import Command, ExecutionInputs, ExecutionReport
from live_tests.commons.utils import get_connector_under_test
from live_tests.debug import DAGGER_CONFIG


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
@click.option(
    "-o",
    "--output-directory",
    help="Directory in which connector output and test results should be stored. Defaults to the current directory.",
    default=Path("live_tests_debug_reports"),
    type=click.Path(file_okay=False, dir_okay=True, resolve_path=True, path_type=Path),
)
@click.option(
    "-hc",
    "--http-cache",
    "enable_http_cache",
    help="Use the HTTP cache for the connector.",
    default=True,
    is_flag=True,
    type=bool,
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
    connector_images: List[str],
    output_directory: Path,
    enable_http_cache: bool,
) -> None:
    output_directory.mkdir(parents=True, exist_ok=True)
    debug_session_start_time = int(time.time())
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
        for connector_image in connector_images:
            try:
                execution_inputs = ExecutionInputs(
                    connector_under_test=await get_connector_under_test(dagger_client, connector_image),
                    command=command,
                    config=connection_objects.source_config,
                    catalog=connection_objects.catalog,
                    state=connection_objects.state,
                    environment_variables=None,
                    enable_http_cache=enable_http_cache,
                )
            except ValueError as e:
                raise click.UsageError(str(e))
            execution_result = await ConnectorRunner(dagger_client, **execution_inputs.to_dict()).run()
            execution_report = ExecutionReport(execution_inputs, execution_result, created_at=debug_session_start_time)
            await execution_report.save_to_disk(output_directory)
