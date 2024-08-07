#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

# HELPERS
from __future__ import annotations

import importlib
import logging
import os
import sys
from typing import TYPE_CHECKING

import asyncclick as click
import requests
from pipelines import main_logger
from pipelines.cli.confirm_prompt import confirm
from pipelines.consts import LOCAL_PIPELINE_PACKAGE_PATH
from pipelines.external_scripts.airbyte_ci_install import RELEASE_URL, get_airbyte_os_name

if TYPE_CHECKING:
    from typing import Callable

__installed_version__ = importlib.metadata.version("pipelines")

PROD_COMMAND = "airbyte-ci"
DEV_COMMAND = "airbyte-ci-dev"
AUTO_UPDATE_AGREE_KEY = "yes_auto_update"


def pre_confirm_auto_update_flag(f: Callable) -> Callable:
    """Decorator to add a --yes-auto-update flag to a command."""
    return click.option(
        "--yes-auto-update/--no-auto-update",
        AUTO_UPDATE_AGREE_KEY,
        is_flag=True,
        default=True,
        help="Skip prompts and automatically upgrade pipelines",
    )(f)


def _is_version_available(version: str, is_dev: bool) -> bool:
    """
    Check if an given version is available.
    """

    # Given that they can install from source, we don't need to check for upgrades
    if is_dev:
        return True

    os_name = get_airbyte_os_name()
    url = f"{RELEASE_URL}/{os_name}/{version}/airbyte-ci"

    # Just check if the URL exists, but dont download it
    return requests.head(url).ok


def _get_latest_version() -> str:
    """
    Get the version of the latest release, which is just in the pyproject.toml file of the pipelines package
    as this is an internal tool, we don't need to check for the latest version on PyPI
    """
    path_to_pyproject_toml = LOCAL_PIPELINE_PACKAGE_PATH + "pyproject.toml"
    with open(path_to_pyproject_toml, "r") as f:
        for line in f.readlines():
            if "version" in line:
                return line.split("=")[1].strip().replace('"', "")
    raise Exception("Could not find version in pyproject.toml. Please ensure you are running from the root of the airbyte repo.")


def is_dev_command() -> bool:
    """
    Check if the current command is the dev version of the command
    """
    current_command = " ".join(sys.argv)
    return DEV_COMMAND in current_command


def check_for_upgrade(
    require_update: bool = True,
    enable_auto_update: bool = True,
) -> None:
    """Check if the installed version of pipelines is up to date."""
    current_command = " ".join(sys.argv)
    latest_version = _get_latest_version()
    is_out_of_date = latest_version != __installed_version__
    if not is_out_of_date:
        main_logger.info(f"airbyte-ci is up to date. Installed version: {__installed_version__}. Latest version: {latest_version}")
        return

    is_dev_version = is_dev_command()
    upgrade_available = _is_version_available(latest_version, is_dev_version)
    if not upgrade_available:
        main_logger.warning(
            f"airbyte-ci is out of date, but no upgrade is available yet. This likely means that a release is still being built. Installed version: {__installed_version__}. Latest version: {latest_version}"
        )
        return

    parent_command = DEV_COMMAND if is_dev_version else PROD_COMMAND
    upgrade_command = f"{parent_command} update"

    # Tack on the specific version if it is not the latest version and it is not the dev version
    # This is because the dev version always corresponds to the version in the local repository
    if not is_dev_version:
        upgrade_command = f"{upgrade_command} --version {latest_version}"

    upgrade_error_message = f"""
    🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨

    This version of `airbyte-ci` does not match that of your local airbyte repository.

    Installed Version: {__installed_version__}.
    Local Repository Version: {latest_version}

    Please upgrade your local airbyte repository to the latest version using the following command:
    $ {upgrade_command}

    Alternatively you can skip this with the `--disable-update-check` flag.

    🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨
    """
    logging.warning(upgrade_error_message)

    # Ask the user if they want to upgrade
    if enable_auto_update and confirm(
        "Do you want to automatically upgrade?", default=True, additional_pre_confirm_key=AUTO_UPDATE_AGREE_KEY
    ):
        # if the current command contains `airbyte-ci-dev` is the dev version of the command
        logging.info(f"[{'DEV' if is_dev_version else 'BINARY'}] Upgrading pipelines...")

        upgrade_exit_code = os.system(upgrade_command)
        if upgrade_exit_code != 0:
            raise Exception(f"Failed to upgrade pipelines. Exit code: {upgrade_exit_code}")

        logging.info(f"Re-running command: {current_command}")

        # Re-run the command
        command_exit_code = os.system(current_command)
        sys.exit(command_exit_code)

    if require_update:
        raise Exception(upgrade_error_message)

    return
