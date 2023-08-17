#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module declares the CLI commands to run the connectors CI pipelines."""


import anyio
import click
from pipelines.builds.cat import run_cat_build_pipeline
from pipelines.contexts import PipelineContext
from pipelines.pipelines.cat import run_cat_pipeline
from pipelines.utils import DaggerPipelineCommand


@click.group(help="Commands related to connector acceptance tests (CAT).")
@click.option(
    "--execute-timeout",
    help="The maximum time in seconds for the execution of a Dagger request before an ExecuteTimeoutError is raised. Passing None results in waiting forever.",
    default=None,
    type=int,
)
@click.pass_context
def cat(
    ctx: click.Context,
    execute_timeout: int,
):
    ctx.obj["execute_timeout"] = execute_timeout


@cat.command(cls=DaggerPipelineCommand, help="Build CAT image.")
@click.pass_context
def build(ctx: click.Context) -> bool:
    """Runs a build pipeline for the selected connectors."""

    context = PipelineContext(
        "Build Connector Acceptance Tests",
        ctx.obj["is_local"],
        ctx.obj["git_branch"],
        ctx.obj["git_revision"],
        ctx.obj.get("gha_workflow_run_url"),
        dagger_logs_url=ctx.obj.get("dagger_logs_url"),
        pipeline_start_timestamp=ctx.obj.get("pipeline_start_timestamp"),
        ci_context=ctx.obj.get("ci_context"),
        is_ci_optional=True,
        ci_report_bucket=ctx.obj["ci_report_bucket_name"],
        ci_gcs_credentials=ctx.obj["ci_gcs_credentials"],
    )
    concurrency = 1
    anyio.run(
        run_cat_pipeline,
        [context],
        run_cat_build_pipeline,
        "Build CAT Pipeline",
        concurrency,
        ctx.obj["dagger_logs_path"],
        ctx.obj["execute_timeout"],
    )

    return True
