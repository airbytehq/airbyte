#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Optional

import asyncclick as click
import semver
from pipelines.airbyte_ci.connectors.bump_version.pipeline import run_connector_version_bump_pipeline
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.pipeline import run_connectors_pipelines
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand


class BumpType(click.ParamType):
    name = "bump-type"

    def __init__(self) -> None:
        self.choices = ["patch", "minor", "major"]

    def convert(self, value: str, param: Optional[click.Parameter], ctx: Optional[click.Context]) -> str:
        if value in self.choices:
            return value
        if value.startswith("version:"):
            version_str = value.split("version:", 1)[1]
            if semver.VersionInfo.is_valid(version_str):
                return value
        self.fail(f"{value} is not a valid bump type. Valid choices are {self.choices} or 'version:<semver-version>'.", param, ctx)

    def __repr__(self) -> str:
        return "BumpType"


@click.command(cls=DaggerPipelineCommand, short_help="Bump a connector version and update its changelog.")
@click.argument("bump-type", type=BumpType())
@click.argument("changelog-entry", type=str)
@click.option("--pr-number", type=int, help="Pull request number.")
@click.pass_context
async def bump_version(
    ctx: click.Context,
    bump_type: str,
    changelog_entry: str,
    pr_number: int | None,
) -> bool:
    """Bump a connector version: update metadata.yaml and changelog."""

    connectors_contexts = [
        ConnectorContext(
            pipeline_name=f"Bump version of connector {connector.technical_name}",
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
            s3_build_cache_access_key_id=ctx.obj.get("s3_build_cache_access_key_id"),
            s3_build_cache_secret_key=ctx.obj.get("s3_build_cache_secret_key"),
            docker_hub_username=ctx.obj.get("docker_hub_username"),
            docker_hub_password=ctx.obj.get("docker_hub_password"),
        )
        for connector in ctx.obj["selected_connectors_with_modified_files"]
    ]

    await run_connectors_pipelines(
        connectors_contexts,
        run_connector_version_bump_pipeline,
        "Version bump pipeline pipeline",
        ctx.obj["concurrency"],
        ctx.obj["dagger_logs_path"],
        ctx.obj["execute_timeout"],
        bump_type,
        changelog_entry,
        pr_number,
    )

    return True
