#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import anyio
import click
from pipelines.bases import CIContext
from pipelines.pipelines.metadata import (
    run_metadata_lib_test_pipeline,
    run_metadata_orchestrator_deploy_pipeline,
    run_metadata_orchestrator_test_pipeline,
)
from pipelines.utils import DaggerPipelineCommand

# MAIN GROUP


@click.group(help="Commands related to the metadata service.")
@click.pass_context
def metadata(ctx: click.Context):
    pass


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
