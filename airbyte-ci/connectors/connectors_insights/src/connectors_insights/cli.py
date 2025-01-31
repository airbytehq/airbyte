# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import asyncclick as click
import asyncer
import dagger
from anyio import Semaphore
from connector_ops.utils import Connector  # type: ignore

from connectors_insights.insights import generate_insights_for_connector
from connectors_insights.result_backends import GCSBucket, LocalDir
from connectors_insights.utils import gcs_uri_to_bucket_key, get_all_connectors_in_directory, remove_strict_encrypt_suffix

if TYPE_CHECKING:
    from typing import List

    from connectors_insights.result_backends import ResultBackend

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


@click.group
async def connectors_insights() -> None:
    pass


@connectors_insights.command("generate", help="Generate connector insights the given connectors.")
@click.option(
    "-n",
    "--name",
    "selected_connectors",
    multiple=True,
    help="The technical name of the connector. e.g. 'source-google-sheets'.",
)
@click.option(
    "-d",
    "--connector-directory",
    "connector_directory",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="The directory containing the connectors, to generate insights for all connectors in this directory.",
)
@click.option(
    "-o",
    "--output-directory",
    "output_directory",
    type=click.Path(file_okay=False, path_type=Path, writable=True, dir_okay=True),
    help="Path to the directory where the insights will be saved as JSON files.",
)
@click.option(
    "-g",
    "--gcs-uri",
    "gcs_uri",
    help="GCS URI to the directory where the insights will be saved as JSON files.",
)
@click.option(
    "-c",
    "--concurrency",
    "concurrency",
    type=int,
    default=5,
    help="The number of connectors to generate insights for concurrently.",
)
@click.option(
    "--rewrite",
    "rewrite",
    type=bool,
    is_flag=True,
    default=False,
    help="Whether to rewrite the report file if it already exists.",
)
async def generate(
    selected_connectors: List[str],
    connector_directory: Path | None,
    output_directory: Path | None,
    gcs_uri: str | None,
    concurrency: int,
    rewrite: bool,
) -> None:
    logger = logging.getLogger(__name__)
    result_backends: List[ResultBackend] = []
    if output_directory:
        result_backends.append(LocalDir(output_directory))
    if gcs_uri:
        result_backends.append(GCSBucket(*gcs_uri_to_bucket_key(gcs_uri)))
    connectors: List[Connector] = []
    if selected_connectors:
        connectors += [Connector(remove_strict_encrypt_suffix(connector)) for connector in selected_connectors]
    if connector_directory:
        connectors += get_all_connectors_in_directory(connector_directory)

    connectors = sorted(list(connectors), key=lambda connector: connector.technical_name, reverse=True)

    if not connectors:
        raise click.UsageError(
            "No connectors passed. Please pass at least one connector with --name or a directory containing connectors with --connector-directory."
        )
    else:
        logger.info(f"Generating insights for {len(connectors)} connectors.")
    semaphore = Semaphore(concurrency)
    soon_results = []
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as dagger_client:
        async with asyncer.create_task_group() as connector_task_group:
            for connector in connectors:
                soon_results.append(
                    connector_task_group.soonify(generate_insights_for_connector)(
                        dagger_client,
                        connector,
                        semaphore,
                        rewrite,
                        result_backends=result_backends,
                    )
                )
    failing_connector_names = [soon_result.value[1].technical_name for soon_result in soon_results if not soon_result.value[0]]
    if failing_connector_names:
        raise click.ClickException("Failed to generate insights for the following connectors: " + ", ".join(failing_connector_names))
