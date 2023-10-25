#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""
Module exposing the tests command to test airbyte-ci projects.
"""

import asyncclick as click
from pipelines.cli.lazy_group import LazyGroup


@click.group(
    cls=LazyGroup,
    help="Commands related to formatting.",
    lazy_subcommands={
        "python": "pipelines.airbyte_ci.format.python.commands.python",
        "java": "pipelines.airbyte_ci.format.java.commands.java",
        "js": "pipelines.airbyte_ci.format.js.commands.js",
    },
)
@click.option("--fix/--check", type=bool, default=None, help="Whether to automatically fix any formatting issues detected.  [required]")
@click.pass_context
def format(ctx: click.Context, fix: bool):
    ctx.obj["fix_formatting"] = fix
