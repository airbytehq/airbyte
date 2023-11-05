# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import logging
import sys
from typing import Any, Dict, List, Optional

import asyncclick as click
import dagger
from pipelines.airbyte_ci.format.consts import DEFAULT_FORMAT_IGNORE_LIST
from pipelines.cli.click_decorators import LazyPassDecorator, click_ignore_unused_kwargs
from pipelines.helpers.utils import sh_dash_c
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext

pass_pipeline_context: LazyPassDecorator = LazyPassDecorator(ClickPipelineContext)


def build_container(
    ctx: ClickPipelineContext, base_image: str, include: List[str], install_commands: List[str], env_vars: Optional[Dict[str, Any]] = {}
) -> dagger.Container:

    dagger_client = ctx.params["dagger_client"]

    base_container = dagger_client.container().from_(base_image)
    for key, value in env_vars.items():
        base_container = base_container.with_env_variable(key, value)

    check_container = (
        base_container.with_mounted_directory(
            "/src",
            dagger_client.host().directory(
                ".",
                include=include,
                exclude=DEFAULT_FORMAT_IGNORE_LIST,
            ),
        )
        .with_exec(sh_dash_c(install_commands))
        .with_workdir("/src")
    )
    return check_container


async def check(
    ctx: ClickPipelineContext,
    base_image: str,
    include: List[str],
    install_commands: List[str],
    check_commands: List[str],
    env_vars: Optional[Dict[str, Any]] = {},
) -> bool:
    """Checks whether the repository is formatted correctly.
    Args:
        ctx: (ClickPipelineContext): The pipeline context
        base_image (str): The base image to use for the container
        include (List[str]): The list of host files to include in the mounted directory
        install_commands (List[str]): The list of commands to run to install the formatter
        check_commands (List[str]): The list of commands to run to check the formatting
        env_vars (Optional[Dict[str, Any]]): A dict of environment variables to set on the container
    Returns:
        bool: True if the check succeeded, false otherwise
    """
    logger = logging.getLogger(f"format")

    container = build_container(ctx, base_image, include, install_commands, check_commands, env_vars)
    try:
        await container.with_exec(sh_dash_c(check_commands))
        return True
    except dagger.ExecError as e:
        logger.error(f"Failed to format code: {e}")
        return False
