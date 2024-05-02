#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import asyncclick as click
from pipelines.airbyte_ci.connectors.check_version_increment.pipeline import VersionIncrementCheck
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.cli.click_decorators import click_ignore_unused_kwargs, click_merge_args_into_context_obj
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand
from pipelines.helpers.execution.run_steps import StepToRun, run_steps
from pipelines.models.contexts.pipeline_context import PipelineContext
from pipelines.models.reports import Report


@click.command(cls=DaggerPipelineCommand, short_help="Check that a connector has a version increment")
@click_merge_args_into_context_obj
@click.pass_context
@click_ignore_unused_kwargs
async def check_version_increment(
    ctx: click.Context,
) -> bool:
    if not ctx.obj["selected_connectors_with_modified_files"]:
        return True
    results = list()
    pipeline_context = PipelineContext(
        pipeline_name="Checking connector version increments",
        is_local=ctx.obj["is_local"],
        git_branch=ctx.obj["git_branch"],
        git_revision=ctx.obj["git_revision"],
        report_output_prefix=ctx.obj["report_output_prefix"],
    )

    for connector in ctx.obj["selected_connectors_with_modified_files"]:
        connector_context = ConnectorContext(
            pipeline_name=f"Checking version increment for connector {connector.technical_name}",
            connector=connector,
            is_local=ctx.obj["is_local"],
            git_branch=ctx.obj["git_branch"],
            git_revision=ctx.obj["git_revision"],
            report_output_prefix=ctx.obj["report_output_prefix"],
        )
        result_dict = await run_steps(
            runnables=[
                StepToRun(id=CONNECTOR_TEST_STEP_ID.VERSION_INC_CHECK, step=VersionIncrementCheck(connector_context)),
            ],
            options=connector_context.run_step_options,
        )
        results += list(result_dict.values())

    report = Report(pipeline_context, steps_results=results, name="Version Increment Check Results")
    pipeline_context.report = report

    return report.success
