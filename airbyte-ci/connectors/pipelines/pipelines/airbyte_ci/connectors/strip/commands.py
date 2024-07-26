#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import asyncclick as click
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.pipeline import run_connectors_pipelines
from pipelines.airbyte_ci.connectors.strip.pipeline import run_connectors_strip_pipeline
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand

@click.command(
    cls=DaggerPipelineCommand,
    short_help="Migrate low-code connector to manifest-only"
  )
@click.pass_context
async def strip(
  ctx: click.Context
) -> bool:
  
  connectors_contexts = [
    ConnectorContext(
      pipeline_name=f"Strip connector {connector.technical_name} to manifest-only",
      connector=connector,
      is_local=ctx.obj["is_local"],
      git_branch=ctx.obj["git_branch"],
      git_revision=ctx.obj["git_revision"],
      diffed_branch=ctx.obj["diffed_branch"],
      git_repo_url=ctx.obj["git_repo_url"],
      report_output_prefix=ctx.obj["report_output_prefix"],
      pipeline_start_timestamp=ctx.obj.get("pipeline_start_timestamp"),
    )
    for connector in ctx.obj["selected_connectors_with_modified_files"]
  ]

  await run_connectors_pipelines(
    connectors_contexts,
    run_connectors_strip_pipeline,
    "Strip connector to manifest-only pipeline",
    ctx.obj["concurrency"],
    ctx.obj["dagger_logs_path"],
    ctx.obj["execute_timeout"],
    ctx.obj["git_branch"],
    ctx.obj["git_revision"],
    ctx.obj["diffed_branch"],
    ctx.obj["is_local"],
    ctx.obj["ci_context"],
    ctx.obj["git_repo_url"],

  )

  return True
