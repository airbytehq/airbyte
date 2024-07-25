#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import asyncclick as click
from pipelines.cli.click_decorators import click_ci_requirements_option
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand

# MAIN GROUP


@click.group(help="Commands related to the metadata service.")
@click_ci_requirements_option()
@click.pass_context
def metadata(ctx: click.Context) -> None:
    pass


@metadata.group(help="Commands related to deploying components of the metadata service.")
@click.pass_context
def deploy(ctx: click.Context) -> None:
    pass


@deploy.command(cls=DaggerPipelineCommand, name="orchestrator", help="Deploy the metadata service orchestrator to production")
@click.pass_context
async def deploy_orchestrator(ctx: click.Context) -> bool:
    # Import locally to speed up CLI.
    from pipelines.airbyte_ci.metadata.pipeline import run_metadata_orchestrator_deploy_pipeline

    return await run_metadata_orchestrator_deploy_pipeline(
        ctx,
        ctx.obj["is_local"],
        ctx.obj["git_branch"],
        ctx.obj["git_revision"],
        ctx.obj["diffed_branch"],
        ctx.obj["git_repo_url"],
        ctx.obj["report_output_prefix"],
        ctx.obj.get("gha_workflow_run_url"),
        ctx.obj.get("dagger_logs_url"),
        ctx.obj.get("pipeline_start_timestamp"),
        ctx.obj.get("ci_context"),
    )
