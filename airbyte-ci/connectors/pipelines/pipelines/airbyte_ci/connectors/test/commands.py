#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import shutil
from typing import Dict, List

import asyncclick as click
from pipelines import main_logger
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.pipeline import run_connectors_pipelines
from pipelines.airbyte_ci.connectors.test.context import ConnectorTestContext
from pipelines.airbyte_ci.connectors.test.pipeline import run_connector_test_pipeline
from pipelines.airbyte_ci.connectors.test.steps.common import RegressionTests
from pipelines.cli.click_decorators import click_ci_requirements_option
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand
from pipelines.consts import LOCAL_BUILD_PLATFORM, MAIN_CONNECTOR_TESTING_SECRET_STORE_ALIAS, ContextState
from pipelines.helpers.execution import argument_parsing
from pipelines.helpers.execution.run_steps import RunStepOptions
from pipelines.helpers.github import update_global_commit_status_check_for_tests
from pipelines.helpers.utils import fail_if_missing_docker_hub_creds
from pipelines.models.secrets import GSMSecretStore
from pipelines.models.steps import STEP_PARAMS

GITHUB_GLOBAL_CONTEXT_FOR_TESTS = "Connectors CI tests"
GITHUB_GLOBAL_DESCRIPTION_FOR_TESTS = "Running connectors tests"


@click.command(
    cls=DaggerPipelineCommand,
    help="Test all the selected connectors.",
    context_settings=dict(
        ignore_unknown_options=True,
    ),
)
@click_ci_requirements_option()
@click.option(
    "--code-tests-only",
    is_flag=True,
    help=("Only execute code tests. " "Metadata checks, QA, and acceptance tests will be skipped."),
    default=False,
    type=bool,
)
@click.option(
    "--fail-fast",
    help="When enabled, tests will fail fast.",
    default=False,
    type=bool,
    is_flag=True,
)
@click.option(
    "--concurrent-cat",
    help="When enabled, the CAT tests will run concurrently. Be careful about rate limits",
    default=False,
    type=bool,
    is_flag=True,
)
@click.option(
    "--skip-step",
    "-x",
    "skip_steps",
    multiple=True,
    type=click.Choice([step_id.value for step_id in CONNECTOR_TEST_STEP_ID]),
    help="Skip a step by name. Can be used multiple times to skip multiple steps.",
)
@click.option(
    "--only-step",
    "-k",
    "only_steps",
    multiple=True,
    type=click.Choice([step_id.value for step_id in CONNECTOR_TEST_STEP_ID]),
    help="Only run specific step by name. Can be used multiple times to keep multiple steps.",
)
@click.option(
    "--global-status-check-context",
    "global_status_check_context",
    help="The context of the global status check which will be sent to GitHub status API.",
    default=GITHUB_GLOBAL_CONTEXT_FOR_TESTS,
)
@click.option(
    "--global-status-check-description",
    "global_status_check_description",
    help="The description of the global status check which will be sent to GitHub status API.",
    default=GITHUB_GLOBAL_DESCRIPTION_FOR_TESTS,
)
@click.argument(
    "extra_params", nargs=-1, type=click.UNPROCESSED, callback=argument_parsing.build_extra_params_mapping(CONNECTOR_TEST_STEP_ID)
)
@click.pass_context
async def test(
    ctx: click.Context,
    code_tests_only: bool,
    fail_fast: bool,
    concurrent_cat: bool,
    skip_steps: List[str],
    only_steps: List[str],
    global_status_check_context: str,
    global_status_check_description: str,
    extra_params: Dict[CONNECTOR_TEST_STEP_ID, STEP_PARAMS],
) -> bool:
    """Runs a test pipeline for the selected connectors.

    Args:
        ctx (click.Context): The click context.
    """
    ctx.obj["global_status_check_context"] = global_status_check_context
    ctx.obj["global_status_check_description"] = global_status_check_description

    if ctx.obj["ci_gcp_credentials"]:
        ctx.obj["secret_stores"][MAIN_CONNECTOR_TESTING_SECRET_STORE_ALIAS] = GSMSecretStore(ctx.obj["ci_gcp_credentials"])
    else:
        main_logger.warn(f"The credentials to connect to {MAIN_CONNECTOR_TESTING_SECRET_STORE_ALIAS} were are not defined.")

    if only_steps and skip_steps:
        raise click.UsageError("Cannot use both --only-step and --skip-step at the same time.")
    if not only_steps:
        skip_steps = list(skip_steps)
        skip_steps += [CONNECTOR_TEST_STEP_ID.CONNECTOR_REGRESSION_TESTS]
    if ctx.obj["is_ci"]:
        fail_if_missing_docker_hub_creds(ctx)

    if ctx.obj["selected_connectors_with_modified_files"]:
        update_global_commit_status_check_for_tests(ctx.obj, "pending")
    else:
        main_logger.warn("No connector were selected for testing.")
        update_global_commit_status_check_for_tests(ctx.obj, "success")
        return True

    run_step_options = RunStepOptions(
        fail_fast=fail_fast,
        skip_steps=[CONNECTOR_TEST_STEP_ID(step_id) for step_id in skip_steps],
        keep_steps=[CONNECTOR_TEST_STEP_ID(step_id) for step_id in only_steps],
        step_params=extra_params,
    )

    connectors_tests_contexts = [
        ConnectorTestContext(
            pipeline_name=f"{global_status_check_context} on {connector.technical_name}",
            connector=connector,
            is_local=ctx.obj["is_local"],
            git_branch=ctx.obj["git_branch"],
            git_revision=ctx.obj["git_revision"],
            diffed_branch=ctx.obj["diffed_branch"],
            git_repo_url=ctx.obj["git_repo_url"],
            ci_git_user=ctx.obj["ci_git_user"],
            ci_github_access_token=ctx.obj["ci_github_access_token"],
            ci_report_bucket=ctx.obj["ci_report_bucket_name"],
            report_output_prefix=ctx.obj["report_output_prefix"],
            gha_workflow_run_url=ctx.obj.get("gha_workflow_run_url"),
            dagger_logs_url=ctx.obj.get("dagger_logs_url"),
            pipeline_start_timestamp=ctx.obj.get("pipeline_start_timestamp"),
            ci_context=ctx.obj.get("ci_context"),
            pull_request=ctx.obj.get("pull_request"),
            ci_gcp_credentials=ctx.obj["ci_gcp_credentials"],
            code_tests_only=code_tests_only,
            use_local_cdk=ctx.obj.get("use_local_cdk"),
            s3_build_cache_access_key_id=ctx.obj.get("s3_build_cache_access_key_id"),
            s3_build_cache_secret_key=ctx.obj.get("s3_build_cache_secret_key"),
            docker_hub_username=ctx.obj.get("docker_hub_username"),
            docker_hub_password=ctx.obj.get("docker_hub_password"),
            concurrent_cat=concurrent_cat,
            run_step_options=run_step_options,
            targeted_platforms=[LOCAL_BUILD_PLATFORM],
            secret_stores=ctx.obj["secret_stores"],
        )
        for connector in ctx.obj["selected_connectors_with_modified_files"]
    ]

    try:
        await run_connectors_pipelines(
            [connector_context for connector_context in connectors_tests_contexts],
            run_connector_test_pipeline,
            "Test Pipeline",
            ctx.obj["concurrency"],
            ctx.obj["dagger_logs_path"],
            ctx.obj["execute_timeout"],
        )
    except Exception as e:
        main_logger.error("An error occurred while running the test pipeline", exc_info=e)
        update_global_commit_status_check_for_tests(ctx.obj, "failure")
        return False

    finally:
        if RegressionTests.regression_tests_artifacts_dir.exists():
            shutil.rmtree(RegressionTests.regression_tests_artifacts_dir)
            main_logger.info(f"  Test artifacts cleaned up from {RegressionTests.regression_tests_artifacts_dir}")

    @ctx.call_on_close
    def send_commit_status_check() -> None:
        if ctx.obj["is_ci"]:
            global_success = all(connector_context.state is ContextState.SUCCESSFUL for connector_context in connectors_tests_contexts)
            update_global_commit_status_check_for_tests(ctx.obj, "success" if global_success else "failure")

    # If we reach this point, it means that all the connectors have been tested so the pipeline did its job and can exit with success.
    return True
