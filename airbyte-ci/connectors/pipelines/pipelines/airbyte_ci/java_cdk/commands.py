#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""
Module exposing the format commands.
"""

from __future__ import annotations

import logging
import sys

import asyncclick as click
from pipelines.cli.click_decorators import click_ci_requirements_option, click_ignore_unused_kwargs, click_merge_args_into_context_obj
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext, pass_pipeline_context


@click.group(name="java-cdk", help="Commands related to the Java CDK")
@click_ci_requirements_option()
@click_merge_args_into_context_obj
@pass_pipeline_context
@click_ignore_unused_kwargs
async def java_cdk(pipeline_context: ClickPipelineContext) -> None:
    pass
