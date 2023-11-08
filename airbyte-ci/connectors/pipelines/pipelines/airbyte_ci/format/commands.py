#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""
Module exposing the format command.
"""

import asyncclick as click
from pipelines.cli.click_decorators import click_ignore_unused_kwargs, click_merge_args_into_context_obj
from pipelines.cli.lazy_group import LazyGroup
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext, pass_pipeline_context


@click.group(
    cls=LazyGroup,
    name="format",
    help="Commands related to formatting.",
    lazy_subcommands={
        "check": "pipelines.airbyte_ci.format.check.commands.check",
        "fix": "pipelines.airbyte_ci.format.fix.commands.fix",
    },
)
@click_merge_args_into_context_obj
@pass_pipeline_context
@click_ignore_unused_kwargs
async def format_code(pipeline_context: ClickPipelineContext):
    pass
