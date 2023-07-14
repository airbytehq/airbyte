#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import anyio
import click
from ci_connector_ops.pipelines.bases import CIContext
from ci_connector_ops.pipelines.pipelines.metadata import (
    run_metadata_lib_test_pipeline,
    run_metadata_orchestrator_deploy_pipeline,
    run_metadata_orchestrator_test_pipeline,
    run_metadata_upload_pipeline,
    run_metadata_validation_pipeline,
)
from ci_connector_ops.pipelines.utils import (
    DaggerPipelineCommand,
    get_all_metadata_files,
    get_expected_metadata_files,
    get_modified_metadata_files,
)

# MAIN GROUP


@click.group(help="Commands related to the metadata service.")
@click.pass_context
def metadata(ctx: click.Context):
    pass


# VALIDATE COMMAND


@metadata.command(cls=DaggerPipelineCommand, help="Commands related to validating the metadata files.")
@click.option("--modified-only/--all", default=True)
@click.pass_context
def validate(ctx: click.Context, modified_only: bool) -> bool:
    if modified_only:
        metadata_to_validate = get_expected_metadata_files(ctx.obj["modified_files"])
    else:
        click.secho("Will run metadata validation on all the metadata files found in the repo.")
        metadata_to_validate = get_all_metadata_files()

    click.secho(f"Will validate {len(metadata_to_validate)} metadata files.")

    return anyio.run(
        run_metadata_validation_pipeline,
        ctx.obj["is_local"],
        ctx.obj["git_branch"],
        ctx.obj["git_revision"],
        ctx.obj.get("gha_workflow_run_url"),
        ctx.obj.get("pipeline_start_timestamp"),
        ctx.obj.get("ci_context"),
        metadata_to_validate,
    )


# UPLOAD COMMAND


@metadata.command(cls=DaggerPipelineCommand, help="Commands related to uploading the metadata files to remote storage.")
@click.argument("gcs-bucket-name", type=click.STRING)
@click.option("--modified-only/--all", default=True)
@click.pass_context
def upload(ctx: click.Context, gcs_bucket_name: str, modified_only: bool) -> bool:
    if modified_only:
        if ctx.obj["ci_context"] is not CIContext.MASTER and ctx.obj["git_branch"] != "master":
            click.secho("Not on the master branch. Skipping metadata upload.")
            return True
        metadata_to_upload = get_modified_metadata_files(ctx.obj["modified_files"])
        if not metadata_to_upload:
            click.secho("No modified metadata found. Skipping metadata upload.")
            return True
    else:
        metadata_to_upload = get_all_metadata_files()

    click.secho(f"Will upload {len(metadata_to_upload)} metadata files.")

    return anyio.run(
        run_metadata_upload_pipeline,
        ctx.obj["is_local"],
        ctx.obj["git_branch"],
        ctx.obj["git_revision"],
        ctx.obj.get("gha_workflow_run_url"),
        ctx.obj.get("dagger_logs_url"),
        ctx.obj.get("pipeline_start_timestamp"),
        ctx.obj.get("ci_context"),
        metadata_to_upload,
        gcs_bucket_name,
    )


# DEPLOY GROUP


@metadata.group(help="Commands related to deploying components of the metadata service.")
@click.pass_context
def deploy(ctx: click.Context):
    pass


@deploy.command(cls=DaggerPipelineCommand, name="orchestrator", help="Deploy the metadata service orchestrator to production")
@click.pass_context
def deploy_orchestrator(ctx: click.Context) -> bool:
    return anyio.run(
        run_metadata_orchestrator_deploy_pipeline,
        ctx.obj["is_local"],
        ctx.obj["git_branch"],
        ctx.obj["git_revision"],
        ctx.obj.get("gha_workflow_run_url"),
        ctx.obj.get("dagger_logs_url"),
        ctx.obj.get("pipeline_start_timestamp"),
        ctx.obj.get("ci_context"),
    )


# TEST GROUP


@metadata.group(help="Commands related to testing the metadata service.")
@click.pass_context
def test(ctx: click.Context):
    pass


@test.command(cls=DaggerPipelineCommand, name="lib", help="Run tests for the metadata service library.")
@click.pass_context
def test_lib(ctx: click.Context) -> bool:
    return anyio.run(
        run_metadata_lib_test_pipeline,
        ctx.obj["is_local"],
        ctx.obj["git_branch"],
        ctx.obj["git_revision"],
        ctx.obj.get("gha_workflow_run_url"),
        ctx.obj.get("dagger_logs_url"),
        ctx.obj.get("pipeline_start_timestamp"),
        ctx.obj.get("ci_context"),
    )


@test.command(cls=DaggerPipelineCommand, name="orchestrator", help="Run tests for the metadata service orchestrator.")
@click.pass_context
def test_orchestrator(ctx: click.Context) -> bool:
    return anyio.run(
        run_metadata_orchestrator_test_pipeline,
        ctx.obj["is_local"],
        ctx.obj["git_branch"],
        ctx.obj["git_revision"],
        ctx.obj.get("gha_workflow_run_url"),
        ctx.obj.get("dagger_logs_url"),
        ctx.obj.get("pipeline_start_timestamp"),
        ctx.obj.get("ci_context"),
    )
