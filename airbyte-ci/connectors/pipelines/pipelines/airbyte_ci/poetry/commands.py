#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""
Module exposing the format commands.
"""

from __future__ import annotations

import asyncclick as click

from pipelines.cli.click_decorators import click_ignore_unused_kwargs, click_merge_args_into_context_obj
from pipelines.cli.lazy_group import LazyGroup
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext, pass_pipeline_context


@click.group(
    name="poetry",
    help="Commands related to running poetry commands.",
    cls=LazyGroup,
    lazy_subcommands={
        "publish": "pipelines.airbyte_ci.poetry.publish.commands.publish",
    },
)
@click.option(
    "--package-path",
    help="The path to publish",
    type=click.STRING,
    required=True,
)
@click_merge_args_into_context_obj
@pass_pipeline_context
@click_ignore_unused_kwargs
async def poetry(pipeline_context: ClickPipelineContext) -> None:
    pass
