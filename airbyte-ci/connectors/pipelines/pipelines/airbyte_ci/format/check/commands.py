from typing import Optional
import asyncclick as click
import dagger
from pipelines.airbyte_ci.format.check.java.commands import java
from pipelines.cli.click_decorators import LazyPassDecorator, click_ignore_unused_kwargs, click_merge_args_into_context_obj
from pipelines.cli.lazy_group import LazyGroup
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext

pass_pipeline_context: LazyPassDecorator = LazyPassDecorator(ClickPipelineContext)


@click.group(
    cls=LazyGroup,
    help="Commands related to formatting.",
    lazy_subcommands={
        "java": "pipelines.airbyte_ci.format.check.java.commands.java",
        # "fix": "pipelines.airbyte_ci.format.fix.commands.fix",
    },
    invoke_without_command=True,
    chain=True,
)
@click_merge_args_into_context_obj
@pass_pipeline_context
@click_ignore_unused_kwargs
async def check(ctx: click.Context, pipeline_ctx: ClickPipelineContext):
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