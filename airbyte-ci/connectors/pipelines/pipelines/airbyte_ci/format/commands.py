#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""
Module exposing the tests command to test airbyte-ci projects.
"""

import asyncclick as click
from pipelines.cli.click_decorators import click_ignore_unused_kwargs, click_merge_args_into_context_obj
from pipelines.cli.lazy_group import LazyGroup


@click.group(
    cls=LazyGroup,
    help="Commands related to formatting.",
    lazy_subcommands={
        "java": "pipelines.airbyte_ci.format.java.commands.java",
        "js": "pipelines.airbyte_ci.format.js.commands.js",
        "license": "pipelines.airbyte_ci.format.license.commands.license",
        "python": "pipelines.airbyte_ci.format.python.commands.python",
    },
    invoke_without_command=True,
)
@click.option("--fix/--check", type=bool, default=None, help="Whether to automatically fix any formatting issues detected.  [required]")
@click_merge_args_into_context_obj
@click_ignore_unused_kwargs
async def format(ctx: click.Context, fix: bool):
    from pipelines.airbyte_ci.format.java.commands import java
    from pipelines.airbyte_ci.format.js.commands import js
    from pipelines.airbyte_ci.format.license.commands import license
    from pipelines.airbyte_ci.format.python.commands import python

    ctx.obj["fix_formatting"] = fix

    if ctx.invoked_subcommand is None:
        # TODO: ctx.forward should forward the fix commands to the subcommands
        await ctx.invoke(license)
        await ctx.invoke(java)
        await ctx.invoke(js)
        await ctx.invoke(python)
