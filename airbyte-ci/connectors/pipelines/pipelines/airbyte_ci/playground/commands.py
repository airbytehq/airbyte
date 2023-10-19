#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import click
from pipelines.stolen.base import PipelineContext
from pipelines.stolen.lazy_decorator import LazyPassDecorator

from pipelines.stolen.settings import GlobalSettings

# Stolen
settings = GlobalSettings()
pass_pipeline_context: LazyPassDecorator = LazyPassDecorator(PipelineContext, global_settings=settings)
pass_global_settings: LazyPassDecorator = LazyPassDecorator(GlobalSettings)

# NEW

@click.command()
@click.argument("arg1")
@click.option("--opt", default="default_value")
@pass_pipeline_context
@pass_global_settings
def playground(
    ctx,
    arg1: str,
    opt: str,
):
    """Runs the tests for the given airbyte-ci package.

    Args:
        poetry_package_path (str): Path to the poetry package to test, relative to airbyte-ci directory.
        test_directory (str): The directory containing the tests to run.
    """
    print(f"playground: {arg1} {opt}")
    print(f"ctx: {dir(ctx)}")
