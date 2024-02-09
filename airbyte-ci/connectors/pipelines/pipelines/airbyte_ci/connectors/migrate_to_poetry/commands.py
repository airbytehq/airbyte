#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import asyncclick as click
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.migrate_to_poetry.pipeline import run_connector_migration_to_poetry_pipeline
from pipelines.airbyte_ci.connectors.pipeline import run_connectors_pipelines
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand
import git
from pathlib import Path

@click.command(
    cls=DaggerPipelineCommand,
    short_help="Migrate the selected connectors to poetry.",
)
@click.pass_context
async def migrate_to_poetry(
    ctx: click.Context,
) -> bool:

    connectors_contexts = [
        ConnectorContext(
            pipeline_name=f"Migrate {connector.technical_name} to Poetry",
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
            enable_report_auto_open=True,
            docker_hub_username=ctx.obj.get("docker_hub_username"),
            docker_hub_password=ctx.obj.get("docker_hub_password"),
            s3_build_cache_access_key_id=ctx.obj.get("s3_build_cache_access_key_id"),
            s3_build_cache_secret_key=ctx.obj.get("s3_build_cache_secret_key"),
        )
        for connector in ctx.obj["selected_connectors_with_modified_files"]
    ]

    await run_connectors_pipelines(
        connectors_contexts,
        run_connector_migration_to_poetry_pipeline,
        "Migration to poetry pipeline",
        ctx.obj["concurrency"],
        ctx.obj["dagger_logs_path"],
        ctx.obj["execute_timeout"],
    )

    ## To commit all file changes in context directory
    airbyte_repo = git.Repo(search_parent_directories=True)

    modified_files = [Path(item.a_path) for item in airbyte_repo.index.diff(None)]
    current_branch = airbyte_repo.active_branch
    created_branches = []
    for connector_context in connectors_contexts:
        new_branch_name = f"{connector_context.connector.technical_name}-poetry"
        if new_branch_name in airbyte_repo.heads:
            connector_context.logger.info(f"Branch {new_branch_name} already exists. Skip creating a new branch.")
            continue

 
        connector_modified_files = False
        for modified_file in modified_files:
            if modified_file.is_relative_to(connector_context.connector.code_directory):
                connector_modified_files = True
                break
        if connector_modified_files:
            airbyte_repo.git.checkout("-b", new_branch_name)
            created_branches.append(new_branch_name)
            airbyte_repo.git.add(str(connector_context.connector.code_directory))
            airbyte_repo.index.commit(f"✨ {connector_context.connector.technical_name}: migrate to poetry")
        current_branch.checkout()
    return True
