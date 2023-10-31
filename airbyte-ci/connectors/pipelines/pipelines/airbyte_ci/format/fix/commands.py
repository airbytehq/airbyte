from typing import Optional
import asyncclick as click
import dagger
from pipelines.cli.click_decorators import LazyPassDecorator, click_ignore_unused_kwargs, click_merge_args_into_context_obj
from pipelines.cli.lazy_group import LazyGroup
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext

pass_pipeline_context: LazyPassDecorator = LazyPassDecorator(ClickPipelineContext)


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
