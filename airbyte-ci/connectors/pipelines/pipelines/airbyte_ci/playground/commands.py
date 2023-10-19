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
@click.argument("hold")
@click.option("--opt", default="default_value")
@pass_pipeline_context
@pass_global_settings
def playground(
    ctx: PipelineContext,
    args,
    **kwargs,
):
    """Runs the tests for the given airbyte-ci package.

    Args:
        poetry_package_path (str): Path to the poetry package to test, relative to airbyte-ci directory.
        test_directory (str): The directory containing the tests to run.
    """

    # ctx = PipelineContext(global_settings=GlobalSettings(PLATFORM='Darwin'), dockerd_service=None, asyncio=<module 'asyncio' from '/Users/ben/.pyenv/versions/3.10.8/lib/python3.10/asyncio/__init__.py'>)
    # args = GlobalSettings(PLATFORM='Darwin')
    # kwargs = {'opt': 'tight', 'hold': 'holdme'}

    import pdb; pdb.set_trace()
    print(f"playground: {args} {kwargs}")
    print(f"ctx: {ctx._click_context().obj}")

    # (Pdb) ctx._click_context().args
    # []
    # (Pdb) ctx._click_context().params
    # {'opt': 'tight', 'hold': 'holdme'}
    # (Pdb)
