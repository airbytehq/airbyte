#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List, Tuple

import asyncclick as click
from click._compat import get_text_stderr
from click.exceptions import UsageError
from pipelines.airbyte_ci.connectors.add_changelog_entries.pipeline import run_connector_add_changelog_entries_pipeline
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.pipeline import run_connectors_pipelines
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand


@click.command(cls=DaggerPipelineCommand, short_help="Add changelog entries to a connector.")
@click.option("--version", type=str)
@click.option(
    "--day-pr-number-and-changelog-entry",
    "days_pr_numbers_and_changelog_entries",
    help="Day, PR number and changelog entry",
    multiple=True,
    type=(str, str, str),
)
@click.pass_context
async def add_changelog_entries(
    ctx: click.Context,
    version: str,
    days_pr_numbers_and_changelog_entries: List[Tuple[str, str, str]],
) -> bool:
    """Bump a connector version: update metadata.yaml and changelog."""
    click.echo(f"SGX version={version}")
    click.echo(f"SGX days_pr_numbers_and_changelog_entries={days_pr_numbers_and_changelog_entries}")
    if version is None:
        click.echo(click.style("Error: Missing option --version!", fg="red", bold=True))
        return False
    if days_pr_numbers_and_changelog_entries is None or days_pr_numbers_and_changelog_entries == ():
        click.echo(click.style("Missing option --day-pr-number-and-changelog-entry!", fg="red", bold=True))
        return False
    connectors = ctx.obj["selected_connectors_with_modified_files"]
    if connectors == []:
        click.echo(click.style("Error: No connector selected!", fg="red", bold=True))
        return False

    connectors_contexts = [
        ConnectorContext(
            pipeline_name=f"Add entries to changelog of connector {connector.technical_name}",
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
            ci_gcs_credentials=ctx.obj["ci_gcs_credentials"],
            ci_git_user=ctx.obj["ci_git_user"],
            ci_github_access_token=ctx.obj["ci_github_access_token"],
            enable_report_auto_open=False,
            s3_build_cache_access_key_id=ctx.obj.get("s3_build_cache_access_key_id"),
            s3_build_cache_secret_key=ctx.obj.get("s3_build_cache_secret_key"),
        )
        for connector in connectors
    ]

    await run_connectors_pipelines(
        connectors_contexts,
        run_connector_add_changelog_entries_pipeline,
        "Connector changelog entry addition pipeline",
        ctx.obj["concurrency"],
        ctx.obj["dagger_logs_path"],
        ctx.obj["execute_timeout"],
        version,
        days_pr_numbers_and_changelog_entries,
    )

    return True
