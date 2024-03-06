# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import asyncclick as click
from live_tests.debug.cli import debug_cmd


@click.group()
@click.pass_context
async def live_tests(ctx):
    pass


live_tests.add_command(debug_cmd)
