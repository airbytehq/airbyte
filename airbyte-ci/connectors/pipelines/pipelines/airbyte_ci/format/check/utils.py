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


async def run_check(
    container: dagger.Container,
    check_commands: List[str],
) -> dagger.Container:
    """Checks whether the repository is formatted correctly.
    Args:
        container: (dagger.Container): The container to run the formatting check in
        check_commands (List[str]): The list of commands to run to check the formatting
    """
    await container.with_exec(sh_dash_c(check_commands))
