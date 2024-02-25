#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Dict, List

import asyncclick as click
from pipelines import main_logger
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.pipeline import run_connectors_pipelines
from pipelines.airbyte_ci.connectors.regression_test.pipeline import run_connector_regression_test_pipeline
from pipelines.cli.click_decorators import click_ci_requirements_option
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand
from pipelines.consts import LOCAL_BUILD_PLATFORM, ContextState
from pipelines.helpers.execution import argument_parsing
from pipelines.helpers.execution.run_steps import RunStepOptions
from pipelines.helpers.github import update_global_commit_status_check_for_tests
from pipelines.helpers.utils import fail_if_missing_docker_hub_creds
from pipelines.models.steps import STEP_PARAMS


@click.command(
    cls=DaggerPipelineCommand,
    help="Test all the selected connectors.",
    context_settings=dict(
        ignore_unknown_options=True,
    ),
)
@click_ci_requirements_option()
@click.option(
    "--control-version",
    help=(
        "Control version of the connector to be tested. Records will be downloaded from this container and used as expected records for the target version."
    ),
    default="latest",
    type=str,
)
@click.option(
    "--target-version",
    help=("Target version of the connector being tested."),
    default="dev",
    type=str,
)
@click.option(
    "--fail-fast",
    help="When enabled, tests will fail fast.",
    default=False,
    type=bool,
    is_flag=True,
)
@click.pass_context
async def regression_test(ctx: click.Context, control_version: str, target_version: str, fail_fast: bool) -> bool:
    """
    Runs a regression test pipeline for the selected connectors.
    """
    if ctx.obj["is_ci"]:
        fail_if_missing_docker_hub_creds(ctx)

    if ctx.obj["selected_connectors_with_modified_files"]:
        update_global_commit_status_check_for_tests(ctx.obj, "pending")
    else:
        main_logger.warn("No connector were selected for testing.")
        update_global_commit_status_check_for_tests(ctx.obj, "success")
        return True

    run_step_options = RunStepOptions(fail_fast=fail_fast)
    connectors_tests_contexts = []
    for connector in ctx.obj["selected_connectors_with_modified_files"]:
        if control_version in ("dev", "latest"):
            control_version = f"airbyte/{connector.technical_name}:{control_version}"

        if target_version in ("dev", "latest"):
            target_version = f"airbyte/{connector.technical_name}:{target_version}"

        connectors_tests_contexts.append(
            ConnectorContext(
                pipeline_name=f"Testing connector {connector.technical_name}",
                connector=connector,
                is_local=ctx.obj["is_local"],
                git_branch=ctx.obj["git_branch"],
                git_revision=ctx.obj["git_revision"],
                ci_report_bucket=ctx.obj["ci_report_bucket_name"],
                report_output_prefix=ctx.obj["report_output_prefix"],
                use_remote_secrets=ctx.obj["use_remote_secrets"],
                gha_workflow_run_url=ctx.obj.get("gha_workflow_run_url"),
                dagger_logs_url=ctx.obj.get("dagger_logs_url"),
                pipeline_start_timestamp=ctx.obj.get("pipeline_start_timestamp"),
                ci_context=ctx.obj.get("ci_context"),
                pull_request=ctx.obj.get("pull_request"),
                ci_gcs_credentials=ctx.obj["ci_gcs_credentials"],
                use_local_cdk=ctx.obj.get("use_local_cdk"),
                s3_build_cache_access_key_id=ctx.obj.get("s3_build_cache_access_key_id"),
                s3_build_cache_secret_key=ctx.obj.get("s3_build_cache_secret_key"),
                docker_hub_username=ctx.obj.get("docker_hub_username"),
                docker_hub_password=ctx.obj.get("docker_hub_password"),
                run_step_options=run_step_options,
                targeted_platforms=[LOCAL_BUILD_PLATFORM],
                versions_to_test=(control_version, target_version),
            )
        )

    try:
        await run_connectors_pipelines(
            [connector_context for connector_context in connectors_tests_contexts],
            run_connector_regression_test_pipeline,
            "Regression Test Pipeline",
            ctx.obj["concurrency"],
            ctx.obj["dagger_logs_path"],
            ctx.obj["execute_timeout"],
        )
    except Exception as e:
        main_logger.error("An error occurred while running the regression test pipeline", exc_info=e)
        return False

    return True
