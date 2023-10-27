#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import asyncclick as click
from pipelines.airbyte_ci.release.pipeline import run_release


@click.command()
async def release():
    """
    TODO
    """
    success = await run_release()
    if not success:
        click.Abort()
