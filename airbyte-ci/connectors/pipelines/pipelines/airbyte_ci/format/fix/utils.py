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


async def run_format(
    container: dagger.Container,
    format_commands: List[str],
) -> dagger.Container:
    """Formats the repository.
    Args:
        container: (dagger.Container): The container to run the formatter in
        format_commands (List[str]): The list of commands to run to format the repository
    """
    format_container = container.with_exec(sh_dash_c(format_commands))
    await format_container.directory("/src").export(".")
