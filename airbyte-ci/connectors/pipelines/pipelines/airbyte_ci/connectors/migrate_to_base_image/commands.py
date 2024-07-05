#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import asyncclick as click
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.migrate_to_base_image.pipeline import run_connector_migration_to_base_image_pipeline
from pipelines.airbyte_ci.connectors.pipeline import run_connectors_pipelines
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand
from pipelines.helpers.utils import fail_if_missing_docker_hub_creds


@click.command(
    cls=DaggerPipelineCommand,
    short_help="Make the selected connectors use our base image: remove dockerfile, update metadata.yaml and update documentation.",
)
@click.option("--pull-request-number", type=str, required=False, default=None)
@click.option(
    "--changelog",
    help="Add message to the changelog.",
    type=bool,
    is_flag=True,
    required=False,
    default=False,
)
@click.option(
    "--bump",
    help="Bump the metadata.yaml version. Can be `major`, `minor`, or `patch`.",
    type=click.Choice(["patch", "minor", "major"]),
    required=False,
    default=None,
)
@click.pass_context
async def migrate_to_base_image(
    ctx: click.Context,
    pull_request_number: str | None,
    changelog: bool,
    bump: str | None,
) -> bool:
    """
    Bump a connector version: update metadata.yaml, changelog and delete legacy files.
    If the `PULL_REQUEST_NUMBER` is not provided, no changelog entry will be added.
    """

    fail_if_missing_docker_hub_creds(ctx)

    connectors_contexts = [
        ConnectorContext(
            pipeline_name=f"Upgrade connector {connector.technical_name} to use our base image",
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
            enable_report_auto_open=False,
            docker_hub_username=ctx.obj.get("docker_hub_username"),
            docker_hub_password=ctx.obj.get("docker_hub_password"),
            s3_build_cache_access_key_id=ctx.obj.get("s3_build_cache_access_key_id"),
            s3_build_cache_secret_key=ctx.obj.get("s3_build_cache_secret_key"),
        )
        for connector in ctx.obj["selected_connectors_with_modified_files"]
    ]

    await run_connectors_pipelines(
        connectors_contexts,
        run_connector_migration_to_base_image_pipeline,
        "Migration to base image pipeline",
        ctx.obj["concurrency"],
        ctx.obj["dagger_logs_path"],
        ctx.obj["execute_timeout"],
    )

    return True
