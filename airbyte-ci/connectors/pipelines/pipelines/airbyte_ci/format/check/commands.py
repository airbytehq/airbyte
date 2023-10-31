from typing import Optional

import asyncclick as click
import dagger
from pipelines.airbyte_ci.format.check.java.commands import java
from pipelines.cli.click_decorators import (
    LazyPassDecorator,
    click_append_to_context_object,
    click_ignore_unused_kwargs,
    click_merge_args_into_context_obj,
)
from pipelines.cli.lazy_group import LazyGroup
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext

pass_pipeline_context: LazyPassDecorator = LazyPassDecorator(ClickPipelineContext)


@click.group(
    cls=LazyGroup,
    help="Run code format checks and fail if any checks fail.",
    lazy_subcommands={
        "java": "pipelines.airbyte_ci.format.check.java.commands.java",
        "js": "pipelines.airbyte_ci.format.check.js.commands.js",
        "license": "pipelines.airbyte_ci.format.check.license.commands.license",
        "python": "pipelines.airbyte_ci.format.check.python.commands.python",
    },
    invoke_without_command=True,
    chain=True,
)
@click_merge_args_into_context_obj
@pass_pipeline_context
@click_ignore_unused_kwargs
async def check(ctx: click.Context, pipeline_ctx: ClickPipelineContext):
    """Run code format checks and fail if any checks fail."""
    # TODO: fix this client hacking
    ctx.obj["dagger_client"] = await pipeline_ctx.get_dagger_client(pipeline_name="Format License")

    # TODO: check should handle async
    # if ctx.invoked_subcommand is None:
    #     dagger_client = await pipeline_ctx.get_dagger_client(pipeline_name="Format All Files")
    #     await ctx.invoke(license, dagger_client)
    #     await ctx.invoke(java, dagger_client)
    #     await ctx.invoke(js, dagger_client)
    #     await ctx.invoke(python, dagger_client)
