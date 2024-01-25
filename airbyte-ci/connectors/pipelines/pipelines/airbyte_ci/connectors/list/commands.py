#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import asyncclick as click
from connector_ops.utils import console  # type: ignore
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand
from rich.table import Table
from rich.text import Text


@click.command(cls=DaggerPipelineCommand, help="List all selected connectors.", name="list")
@click.pass_context
async def list_connectors(
    ctx: click.Context,
) -> bool:
    selected_connectors = sorted(ctx.obj["selected_connectors_with_modified_files"], key=lambda x: x.technical_name)
    table = Table(title=f"{len(selected_connectors)} selected connectors")
    table.add_column("Modified")
    table.add_column("Connector")
    table.add_column("Language")
    table.add_column("Release stage")
    table.add_column("Version")
    table.add_column("Folder")

    for connector in selected_connectors:
        modified = "X" if connector.modified_files else ""
        connector_name = Text(connector.technical_name)
        language: Text = Text(connector.language.value) if connector.language else Text("N/A")
        try:
            support_level: Text = Text(connector.support_level)
        except Exception:
            support_level = Text("N/A")
        try:
            version: Text = Text(connector.version)
        except Exception:
            version = Text("N/A")
        folder = Text(str(connector.code_directory))
        table.add_row(modified, connector_name, language, support_level, version, folder)

    console.print(table)
    return True
