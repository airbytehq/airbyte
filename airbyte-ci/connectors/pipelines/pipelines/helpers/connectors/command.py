# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import TYPE_CHECKING, Any, Callable, List

import asyncclick as click
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.pipeline import run_connectors_pipelines
from pipelines.airbyte_ci.connectors.reports import ConnectorReport, Report
from pipelines.helpers.execution.run_steps import STEP_TREE, run_steps
from pipelines.models.steps import Step, StepStatus

if TYPE_CHECKING:
    from anyio import Semaphore


def get_connector_contexts(ctx: click.Context, pipeline_description: str, enable_report_auto_open: bool) -> List[ConnectorContext]:
    connectors_contexts = [
        ConnectorContext(
            pipeline_name=f"{pipeline_description}: {connector.technical_name}",
            connector=connector,
            is_local=ctx.obj["is_local"],
            git_branch=ctx.obj["git_branch"],
            git_revision=ctx.obj["git_revision"],
            diffed_branch=ctx.obj["diffed_branch"],
            git_repo_url=ctx.obj["git_repo_url"],
            ci_report_bucket=ctx.obj["ci_report_bucket_name"],
            report_output_prefix=ctx.obj["report_output_prefix"],
            gha_workflow_run_url=ctx.obj.get("gha_workflow_run_url"),
            dagger_logs_url=ctx.obj.get("dagger_logs_url"),
            pipeline_start_timestamp=ctx.obj.get("pipeline_start_timestamp"),
            ci_context=ctx.obj.get("ci_context"),
            ci_gcp_credentials=ctx.obj["ci_gcp_credentials"],
            ci_git_user=ctx.obj["ci_git_user"],
            ci_github_access_token=ctx.obj["ci_github_access_token"],
            enable_report_auto_open=enable_report_auto_open,
            docker_hub_username=ctx.obj.get("docker_hub_username"),
            docker_hub_password=ctx.obj.get("docker_hub_password"),
            s3_build_cache_access_key_id=ctx.obj.get("s3_build_cache_access_key_id"),
            s3_build_cache_secret_key=ctx.obj.get("s3_build_cache_secret_key"),
        )
        for connector in ctx.obj["selected_connectors_with_modified_files"]
    ]
    return connectors_contexts


async def run_connector_pipeline(
    ctx: click.Context,
    pipeline_description: str,
    enable_report_auto_open: bool,
    connector_pipeline: Callable,
    *args: Any,
) -> bool:
    connectors_contexts = get_connector_contexts(ctx, pipeline_description, enable_report_auto_open=enable_report_auto_open)
    await run_connectors_pipelines(
        connectors_contexts,
        connector_pipeline,
        pipeline_description,
        ctx.obj["concurrency"],
        ctx.obj["dagger_logs_path"],
        ctx.obj["execute_timeout"],
        *args,
    )

    return True


async def run_connector_steps(
    context: ConnectorContext, semaphore: "Semaphore", steps_to_run: STEP_TREE, restore_original_state: Step | None = None
) -> Report:
    async with semaphore:
        async with context:
            try:
                result_dict = await run_steps(
                    runnables=steps_to_run,
                    options=context.run_step_options,
                )
            except Exception as e:
                if restore_original_state:
                    await restore_original_state.run()
                raise e
            results = list(result_dict.values())
            if restore_original_state:
                if any(step_result.status is StepStatus.FAILURE for step_result in results):
                    await restore_original_state.run()
                else:
                    # cleanup if available
                    if hasattr(restore_original_state, "_cleanup"):
                        method = getattr(restore_original_state, "_cleanup")
                        if callable(method):
                            await method()

            report = ConnectorReport(context, steps_results=results, name="TEST RESULTS")
            context.report = report
    return report
