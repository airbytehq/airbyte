# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""CLI commands for `airbyte-cdk`.

This CLI interface allows you to interact with your connector, including
testing and running commands.

**Basic Usage:**

```bash
airbyte-cdk --help
airbyte-cdk --version
airbyte-cdk connector --help
airbyte-cdk manifest --help
```

**Running Statelessly:**

You can run the latest version of this CLI, from any machine, using `pipx` or `uvx`:

```bash
# Run the latest version of the CLI:
pipx run airbyte-cdk connector --help
uvx airbyte-cdk connector --help

# Run from a specific CDK version:
pipx run airbyte-cdk==6.5.1 connector --help
uvx airbyte-cdk==6.5.1 connector --help
```

**Running within your virtualenv:**

You can also run from your connector's virtualenv:

```bash
poetry run airbyte-cdk connector --help
```

"""

from typing import cast

import rich_click as click

from airbyte_cdk.cli.airbyte_cdk._connector import connector_cli_group
from airbyte_cdk.cli.airbyte_cdk._image import image_cli_group
from airbyte_cdk.cli.airbyte_cdk._manifest import manifest_cli_group
from airbyte_cdk.cli.airbyte_cdk._secrets import secrets_cli_group
from airbyte_cdk.cli.airbyte_cdk._version import print_version


@click.group(
    help=__doc__.replace("\n", "\n\n"),  # Render docstring as help text (markdown)
    invoke_without_command=True,
)
@click.option(
    "--version",
    is_flag=True,
    help="Show the version of the Airbyte CDK.",
)
@click.pass_context
def cli(
    ctx: click.Context,
    version: bool,
) -> None:
    """Airbyte CDK CLI.

    Help text is provided from the file-level docstring.
    """
    if version:
        print_version(short=False)
        ctx.exit()

    if ctx.invoked_subcommand is None:
        # If no subcommand is provided, show the help message.
        click.echo(ctx.get_help())
        ctx.exit()


cli.add_command(connector_cli_group)
cli.add_command(manifest_cli_group)
cli.add_command(image_cli_group)
cli.add_command(secrets_cli_group)


if __name__ == "__main__":
    cli()
