# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import logging
import sys
from typing import Optional

import asyncclick as click
import dagger
from pipelines.airbyte_ci.format.check.utils import check
from pipelines.airbyte_ci.format.consts import DEFAULT_FORMAT_IGNORE_LIST
from pipelines.cli.click_decorators import click_ignore_unused_kwargs
from pipelines.helpers.utils import sh_dash_c
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext, pass_pipeline_context


@click.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def js(ctx: ClickPipelineContext):
    """Format yaml and json code via prettier."""
    success = await check(
        ctx,
        base_image="node:18.18.0-slim",
        include=["**/*.yaml", "**/*.yml", "**.*/json", "package.json", "package-lock.json"],
        install_commands=["npm install -g npm@10.1.0", "npm install -g prettier@2.8.1"],
        check_commands=["prettier --check ."],
    )
    if not success:
        sys.exit(1)
