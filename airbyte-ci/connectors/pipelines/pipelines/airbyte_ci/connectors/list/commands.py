#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from pathlib import Path

import asyncclick as click
from connector_ops.utils import console  # type: ignore
from rich.table import Table
from rich.text import Text

from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand


@click.command(cls=DaggerPipelineCommand, help="List all selected connectors.", name="list")
@click.option(
    "-o",
    "--output",
    "output_path",
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
    help="Path where the JSON output will be saved.",
)
@click.pass_context
async def list_connectors(
    ctx: click.Context,
    output_path: Path,
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
    if output_path:
        with open(output_path, "w") as f:
            json.dump([connector.technical_name for connector in selected_connectors], f)
    console.print(table)
    return True
