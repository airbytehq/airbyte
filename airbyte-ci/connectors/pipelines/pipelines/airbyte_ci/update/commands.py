#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

import asyncclick as click
from pipelines.cli.auto_update import is_dev_command
from pipelines.external_scripts.airbyte_ci_dev_install import main as install_airbyte_ci_dev_pipx
from pipelines.external_scripts.airbyte_ci_install import main as install_airbyte_ci_binary


@click.command()
@click.option("--version", default="latest", type=str, help="The version to update to.")
async def update(version: str) -> None:
    """Updates airbyte-ci to the latest version."""
    is_dev = is_dev_command()
    if is_dev:
        logging.info("Updating to the latest development version of airbyte-ci...")
        install_airbyte_ci_dev_pipx()
    else:
        logging.info("Updating to the latest version of airbyte-ci...")
        install_airbyte_ci_binary(version)
