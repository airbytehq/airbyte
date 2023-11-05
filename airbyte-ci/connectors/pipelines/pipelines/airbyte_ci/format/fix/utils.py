# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import logging
import sys
from typing import Any, Dict, List, Optional

import asyncclick as click
import dagger
from pipelines.airbyte_ci.format.check.utils import build_container
from pipelines.airbyte_ci.format.consts import DEFAULT_FORMAT_IGNORE_LIST
from pipelines.cli.click_decorators import LazyPassDecorator, click_ignore_unused_kwargs
from pipelines.helpers.utils import sh_dash_c
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext

pass_pipeline_context: LazyPassDecorator = LazyPassDecorator(ClickPipelineContext)


async def format(
    ctx: ClickPipelineContext,
    base_image: str,
    include: List[str],
    install_commands: List[str],
    format_commands: List[str],
    env_vars: Optional[Dict[str, Any]] = {},
) -> bool:
    """Formats the repository.
    Args:
        ctx: (ClickPipelineContext): The pipeline context
        base_image (str): The base image to use for the container
        include (List[str]): The list of host files to include in the mounted directory
        install_commands (List[str]): The list of commands to run to install the formatter
        format_commands (List[str]): The list of commands to run to check the formatting
        env_vars (Optional[Dict[str, Any]]): A dict of environment variables to set on the container
    Returns:
        bool: True if the check succeeded, false otherwise
    """
    container = build_container(ctx, base_image, include, install_commands, env_vars)

    format_container = container.with_exec(sh_dash_c(format_commands))
    await format_container.directory("/src").export(".")
