#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging

import anyio
import click
from ci_connector_ops.pipelines.contexts import CIContext
from ci_connector_ops.pipelines.pipelines.metadata import (
    run_metadata_lib_test_pipeline,
    run_metadata_orchestrator_test_pipeline,
    run_metadata_upload_pipeline,
    run_metadata_validation_pipeline,
)
from ci_connector_ops.pipelines.utils import DaggerPipelineCommand, get_modified_connectors, get_modified_files_per_connector
from ci_connector_ops.utils import get_all_released_connectors
from rich.logging import RichHandler

logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)])
logger = logging.getLogger(__name__)

# MAIN GROUP


@click.group(help="Commands related to the metadata service.")
@click.pass_context
def metadata(ctx: click.Context):
    pass


# VALIDATE COMMAND


@metadata.command(cls=DaggerPipelineCommand, help="Commands related to validating the metadata files.")
@click.pass_context
def validate(ctx: click.Context):
    modified_files = ctx.obj["modified_files_in_branch"]
    modified_connectors = get_modified_connectors(modified_files)

    if not modified_connectors:
        click.secho("No modified connectors found. Skipping metadata validation.")
        return

    metadata_connectors = [connector.technical_name for connector in modified_connectors]
    metadata_source_paths = [connector.code_directory for connector in modified_connectors]

    click.secho(f"Validating metadata for the following connectors: {', '.join(metadata_connectors)}")

    return anyio.run(
        run_metadata_validation_pipeline,
        ctx.obj["is_local"],
        ctx.obj["git_branch"],
        ctx.obj["git_revision"],
        ctx.obj.get("gha_workflow_run_url"),
        ctx.obj.get("pipeline_start_timestamp"),
        ctx.obj.get("ci_context"),
        metadata_source_paths,
    )


# UPLOAD COMMAND


@metadata.command(cls=DaggerPipelineCommand, help="Commands related to uploading the metadata files to remote storage.")
@click.argument("gcs-bucket-name", type=click.STRING)
@click.option(
    "--gcs-credentials", help="Credentials in JSON format with permission to get and upload on the GCS bucket", envvar="GCS_CREDENTIALS"
)
@click.option("--modified-only/--all", default=True)
@click.pass_context
def upload(ctx: click.Context, gcs_bucket_name: str, gcs_credentials: str, modified_only: bool):
    if modified_only:
        if ctx.obj["ci_context"] is not CIContext.MASTER and ctx.obj["git_branch"] != "master":
            click.secho("Not on the master branch. Skipping metadata upload.")
            return
        modified_files = ctx.obj["modified_files_in_commit"]
        modified_metadata_per_connector = get_modified_files_per_connector(modified_files, "metadata.yaml")
        if not modified_metadata_per_connector:
            click.secho("No modified metadata found. Skipping metadata upload.")
            return
        connectors = list(modified_metadata_per_connector.keys())
    else:
        connectors = get_all_released_connectors()

    connectors_name = [c.technical_name for c in connectors]

    click.secho(f"Uploading metadata for the following connectors: {', '.join(connectors_name)}")

    return anyio.run(
        run_metadata_upload_pipeline,
        ctx.obj["is_local"],
        ctx.obj["git_branch"],
        ctx.obj["git_revision"],
        ctx.obj.get("gha_workflow_run_url"),
        ctx.obj.get("pipeline_start_timestamp"),
        ctx.obj.get("ci_context"),
        connectors,
        gcs_bucket_name,
        gcs_credentials,
    )


# TEST GROUP


@metadata.group(help="Commands related to testing the metadata service.")
@click.pass_context
def test(ctx: click.Context):
    pass


@test.command(cls=DaggerPipelineCommand, help="Run tests for the metadata service library.")
@click.pass_context
def lib(ctx: click.Context):
    return anyio.run(
        run_metadata_lib_test_pipeline,
        ctx.obj["is_local"],
        ctx.obj["git_branch"],
        ctx.obj["git_revision"],
        ctx.obj.get("gha_workflow_run_url"),
        ctx.obj.get("pipeline_start_timestamp"),
        ctx.obj.get("ci_context"),
    )


@test.command(cls=DaggerPipelineCommand, help="Run tests for the metadata service orchestrator.")
@click.pass_context
def orchestrator(ctx: click.Context):
    return anyio.run(
        run_metadata_orchestrator_test_pipeline,
        ctx.obj["is_local"],
        ctx.obj["git_branch"],
        ctx.obj["git_revision"],
        ctx.obj.get("gha_workflow_run_url"),
        ctx.obj.get("pipeline_start_timestamp"),
        ctx.obj.get("ci_context"),
    )


if __name__ == "__main__":
    lib()
