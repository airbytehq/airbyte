# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import time
from pathlib import Path
from typing import List, Optional

import asyncclick as click
import dagger
from airbyte_protocol.models import ConfiguredAirbyteCatalog  # type: ignore
from live_tests.commons.connector_runner import ConnectorRunner
from live_tests.commons.models import Command, ExecutionInputs, ExecutionReport
from live_tests.commons.utils import get_connector_config, get_connector_under_test, get_state
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
    "--config-path",
    help="Path to the connector config.",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True, path_type=Path),
)
@click.option(
    "--catalog-path",
    help="Path to the connector catalog.",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True, path_type=Path),
)
@click.option(
    "--state-path",
    help="Path to the connector state.",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True, path_type=Path),
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
    connector_images: List[str],
    output_directory: Path,
    config_path: Optional[str],
    catalog_path: Optional[str],
    state_path: Optional[str],
    enable_http_cache: bool,
) -> None:
    output_directory.mkdir(parents=True, exist_ok=True)
    debug_session_start_time = int(time.time())
    async with dagger.Connection(config=DAGGER_CONFIG) as dagger_client:
        for connector_image in connector_images:
            try:
                execution_inputs = ExecutionInputs(
                    connector_under_test=await get_connector_under_test(dagger_client, connector_image),
                    command=command,
                    config=get_connector_config(config_path),
                    catalog=ConfiguredAirbyteCatalog.parse_file(catalog_path) if catalog_path else None,
                    state=get_state(state_path) if state_path else None,
                    environment_variables=None,
                    enable_http_cache=enable_http_cache,
                )
            except ValueError as e:
                raise click.UsageError(str(e))
            execution_result = await ConnectorRunner(dagger_client, **execution_inputs.to_dict()).run()
            execution_report = ExecutionReport(execution_inputs, execution_result, created_at=debug_session_start_time)
            await execution_report.save_to_disk(output_directory)
