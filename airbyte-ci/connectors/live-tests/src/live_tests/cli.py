# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import asyncclick as click
from live_tests.debug.cli import debug_cmd


@click.group()
@click.pass_context
async def live_tests(ctx: click.Context) -> None:
    pass


live_tests.add_command(debug_cmd)
