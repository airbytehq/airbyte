# HELPERS

import importlib
import logging
import os
import sys

import asyncclick as click
import requests
from pipelines import main_logger
from pipelines.consts import LOCAL_PIPELINE_PACKAGE_PATH

__installed_version__ = importlib.metadata.version("pipelines")

BINARY_UPGRADE_COMMAND = "make tools.airbyte-ci.install"
DEV_UPGRADE_COMMAND = "make tools.airbyte-ci-dev.install"


def _get_os_name():
    """
    Returns 'ubuntu' if the system is Linux or 'macos' if the system is macOS.
    """
    OS = os.uname().sysname
    if OS == "Linux":
        return "ubuntu"
    elif OS == "Darwin":
        return "macos"
    else:
        # Default to macos as this is just a check, if they are not supported they will find
        # out at install time.
        return "macos"


def _is_version_available(version: str, is_dev: bool) -> bool:
    """
    Check if an upgrade is available for the given version.
    """

    # Given that they can install from source, we don't need to check for upgrades
    if is_dev:
        return True

    # Get RELEASE_URL from the environment if it exists, otherwise use the default
    # "https://connectors.airbyte.com/files/airbyte-ci/releases"
    release_url = os.getenv("RELEASE_URL", "https://connectors.airbyte.com/files/airbyte-ci/releases")
    os_name = _get_os_name()
    url = f"{release_url}/{os_name}/{version}/airbyte-ci"

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


def check_for_upgrade(
    require_update=True,
    enable_auto_update=True,
):
    """Check if the installed version of pipelines is up to date."""
    current_command = " ".join(sys.argv)
    latest_version = _get_latest_version()
    is_out_of_date = latest_version != __installed_version__
    is_dev_version = "airbyte-ci-dev" in current_command

    upgrade_command = DEV_UPGRADE_COMMAND if is_dev_version else f"{BINARY_UPGRADE_COMMAND} VERSION={latest_version}"

    if not is_out_of_date:
        main_logger.info(f"airbyte-ci is up to date. Installed version: {__installed_version__}. Latest version: {latest_version}")
        return

    upgrade_available = _is_upgrade_available(latest_version, is_dev_version)
    if not upgrade_available:
        main_logger.warning(
            f"airbyte-ci is out of date, but no upgrade is available yet. This likely means that a release is still being built. Installed version: {__installed_version__}. Latest version: {latest_version}"
        )
        return

    upgrade_error_message = f"""
    🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨

    This version of `airbyte-ci` does not match that of your local airbyte repository.

    Installed Version: {__installed_version__}.
    Local Repository Version: {latest_version}

    Please upgrade your local airbyte repository to the latest version using the following command:
    {upgrade_command}

    🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨
    """
    logging.warning(upgrade_error_message)

    # Ask the user if they want to upgrade
    if enable_auto_update and click.confirm("Do you want to automatically upgrade?", default=True):
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
