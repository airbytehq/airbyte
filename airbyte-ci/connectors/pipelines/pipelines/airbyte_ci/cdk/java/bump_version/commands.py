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
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand
from pipelines.cli.lazy_group import LazyGroup
from pipelines.helpers.connectors.modifed import ConnectorWithModifiedFiles, get_connector_modified_files, get_modified_connectors
from pipelines.helpers.git import get_modified_files
from pipelines.helpers.utils import transform_strs_to_paths


@click.command(cls=DaggerPipelineCommand, short_help="Bump the Java CDK version: update version.properties and changelog.")
@click_merge_args_into_context_obj
@click.pass_context
@click_ignore_unused_kwargs
async def bump_version(
    ctx: click.Context,
) -> bool:
    print("SGX executing cdk java bump_version command")
    return True
