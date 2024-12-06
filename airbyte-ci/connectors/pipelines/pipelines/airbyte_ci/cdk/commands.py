#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
from pathlib import Path
from typing import List, Optional, Set, Tuple

import asyncclick as click
from connector_ops.utils import ConnectorLanguage, SupportLevelEnum, get_all_connectors_in_repo  # type: ignore
from pipelines import main_logger
from pipelines.cli.click_decorators import click_append_to_context_object, click_ignore_unused_kwargs, click_merge_args_into_context_obj
from pipelines.cli.lazy_group import LazyGroup
from pipelines.helpers.connectors.modifed import ConnectorWithModifiedFiles, get_connector_modified_files, get_modified_connectors
from pipelines.helpers.git import get_modified_files
from pipelines.helpers.utils import transform_strs_to_paths


@click.group(
    cls=LazyGroup,
    help="Commands related to connectors and connector acceptance tests.",
    lazy_subcommands={
        "java": "pipelines.airbyte_ci.cdk.java.commands.java",
    },
)
@click_merge_args_into_context_obj
@click.pass_context
@click_ignore_unused_kwargs
async def cdk(
    ctx: click.Context,
) -> None:
    print("SGX executing cdk command")
