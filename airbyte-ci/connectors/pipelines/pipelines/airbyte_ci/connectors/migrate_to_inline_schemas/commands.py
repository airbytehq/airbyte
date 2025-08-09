#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import asyncclick as click

from pipelines.airbyte_ci.connectors.migrate_to_inline_schemas.pipeline import run_connector_migrate_to_inline_schemas_pipeline
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand
from pipelines.helpers.connectors.command import run_connector_pipeline
from pipelines.helpers.connectors.format import verify_formatters


@click.command(
    cls=DaggerPipelineCommand,
    short_help="Where possible (have a metadata.yaml), move stream schemas to inline schemas.",
)
@click.option(
    "--report",
    is_flag=True,
    type=bool,
    default=False,
    help="Auto open report browser.",
)
@click.pass_context
async def migrate_to_inline_schemas(ctx: click.Context, report: bool) -> bool:
    verify_formatters()
    return await run_connector_pipeline(
        ctx,
        "Migrate to inline schemas",
        report,
        run_connector_migrate_to_inline_schemas_pipeline,
    )
