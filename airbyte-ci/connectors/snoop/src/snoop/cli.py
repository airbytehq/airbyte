# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import os
from pathlib import Path
import sys
import typing


import click

from snoop.session import Session
from snoop import runners, collectors, utils, logger

if typing.TYPE_CHECKING:
    from typing import Tuple



def patch_args_to_add_absolute_paths(args):
    patched_args = [args[0]]
    for arg in args[1:]:
        if arg.startswith("--") or arg.startswith("/"):
            patched_args.append(arg)
        else:
            patched_args.append(f"/config/{arg}")
    return patched_args


@click.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.pass_context
def snoop(ctx: click.Context):
    airbyte_command = ctx.args[0]
    entrypoint_args = patch_args_to_add_absolute_paths(ctx.args)
    
    connector_metadata = utils.get_connector_metadata()

    config_collector = collectors.ConnectorConfigCollector(entrypoint_args)
    message_collector = collectors.ConnectorMessageCollector(config_collector.catalog_path)
    
    connector_command = runners.get_connector_command(entrypoint_args)
    connector_command_runner = runners.CommandRunner(connector_command, callback=message_collector.collect)
    
    with Session(airbyte_command, connector_metadata, connector_command_runner, config_collector, message_collector) as snoop_session:
        logger.info(f"Starting {airbyte_command} snoop session")
    sys.exit(snoop_session.exit_code)