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
async def python(ctx: ClickPipelineContext):
    """Format python code via black and isort."""
    success = await check(
        ctx,
        base_image="python:3.10.13-slim",
        env_vars={"PIPX_BIN_DIR": "/usr/local/bin"},
        include=["**/*.py", "pyproject.toml", "poetry.lock"],
        install_commands=["pip install pipx", "pipx ensurepath", "pipx install poetry"],
        check_commands=[
            "poetry install",
            "poetry run isort --settings-file pyproject.toml --check-only .",
            "poetry run black --config pyproject.toml --check .",
        ],
    )
    if not success:
        sys.exit(1)
