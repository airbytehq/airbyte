#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""
Module exposing the tests command to test airbyte-ci projects.
"""

from typing import Optional
import asyncclick as click
import dagger
from pipelines.cli.click_decorators import LazyPassDecorator, click_ignore_unused_kwargs, click_merge_args_into_context_obj
from pipelines.cli.lazy_group import LazyGroup
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext

pass_pipeline_context: LazyPassDecorator = LazyPassDecorator(ClickPipelineContext)

@click.group(
    cls=LazyGroup,
    help="Commands related to formatting.",
    lazy_subcommands={
        "check": "pipelines.airbyte_ci.format.commands.check",
        "fix": "pipelines.airbyte_ci.format.commands.fix",
    },
    invoke_without_command=True,
)
@click_merge_args_into_context_obj
@pass_pipeline_context
@click_ignore_unused_kwargs
async def format(ctx: click.Context, pipeline_ctx: ClickPipelineContext):
    pass

@click.group(chain=True)
@pass_pipeline_context
@click_ignore_unused_kwargs
async def check(ctx: ClickPipelineContext):
    """Run code format checks and fail if any checks fail."""
    print("check group")
    # TODO: check should handle async

    # if ctx.invoked_subcommand is None:
    #     dagger_client = await pipeline_ctx.get_dagger_client(pipeline_name="Format All Files")
    #     await ctx.invoke(license, dagger_client)
    #     await ctx.invoke(java, dagger_client)
    #     await ctx.invoke(js, dagger_client)
    #     await ctx.invoke(python, dagger_client)



@check.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def java(ctx: ClickPipelineContext):
    """Run code format checks and fail if any checks fail."""
    print("checking java")

@check.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def js(ctx: ClickPipelineContext):
    """Run code format checks and fail if any checks fail."""
    print("checking js")

@check.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def license(ctx: ClickPipelineContext):
    """Run code format checks and fail if any checks fail."""
    print("checking license")

@check.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def python(ctx: ClickPipelineContext):
    """Run code format checks and fail if any checks fail."""
    print("checking python")




@click.group(chain=True)
@pass_pipeline_context
@click_ignore_unused_kwargs
async def fix(ctx: ClickPipelineContext):
    """Run code format checks and fix any failures."""
    print("fix group")

    # if ctx.invoked_subcommand is None:
    #     dagger_client = await pipeline_ctx.get_dagger_client(pipeline_name="Format All Files")
    #     await ctx.invoke(license, dagger_client)
    #     await ctx.invoke(java, dagger_client)
    #     await ctx.invoke(js, dagger_client)
    #     await ctx.invoke(python, dagger_client)

@fix.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def java(ctx: ClickPipelineContext):
    """Run code format checks and fix any failures."""
    print("fixing java")

@fix.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def js(ctx: ClickPipelineContext):
    """Run code format checks and fix any failures."""
    print("fixing js")

@fix.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def license(ctx: ClickPipelineContext):
    """Run code format checks and fix any failures."""
    print("fixing license")

@fix.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def python(ctx: ClickPipelineContext):
    """Run code format checks and fix any failures."""
    print("fixing python")
