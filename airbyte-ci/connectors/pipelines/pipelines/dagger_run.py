#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module execute the airbyte-ci-internal CLI wrapped in a dagger run command to use the Dagger Terminal UI."""

import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

import pkg_resources
import requests

LOGGER = logging.getLogger(__name__)
BIN_DIR = Path.home() / "bin"
BIN_DIR.mkdir(exist_ok=True)
DAGGER_CLOUD_TOKEN_ENV_VAR_NAME_VALUE = (
    "_EXPERIMENTAL_DAGGER_CLOUD_TOKEN",
    "p.eyJ1IjogIjFiZjEwMmRjLWYyZmQtNDVhNi1iNzM1LTgxNzI1NGFkZDU2ZiIsICJpZCI6ICJlNjk3YzZiYy0yMDhiLTRlMTktODBjZC0yNjIyNGI3ZDBjMDEifQ.hT6eMOYt3KZgNoVGNYI3_v4CC-s19z8uQsBkGrBhU3k",
)
ARGS_DISABLING_TUI = ["--no-tui", "publish"]


def get_dagger_path() -> Optional[str]:
    try:
        return (
            subprocess.run(["which", "dagger"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode("utf-8").strip()
        )
    except subprocess.CalledProcessError:
        if Path(BIN_DIR / "dagger").exists():
            return str(Path(BIN_DIR / "dagger"))


def get_current_dagger_sdk_version() -> str:
    version = pkg_resources.get_distribution("dagger-io").version
    return version


def install_dagger_cli(dagger_version: str) -> None:
    install_script_path = "/tmp/install_dagger.sh"
    with open(install_script_path, "w") as f:
        response = requests.get("https://dl.dagger.io/dagger/install.sh")
        response.raise_for_status()
        f.write(response.text)
    subprocess.run(["chmod", "+x", install_script_path], check=True)
    os.environ["BIN_DIR"] = str(BIN_DIR)
    os.environ["DAGGER_VERSION"] = dagger_version
    subprocess.run([install_script_path], check=True)


def get_dagger_cli_version(dagger_path: Optional[str]) -> Optional[str]:
    if not dagger_path:
        return None
    version_output = (
        subprocess.run([dagger_path, "version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode("utf-8").strip()
    )
    version_pattern = r"v(\d+\.\d+\.\d+)"

    match = re.search(version_pattern, version_output)

    if match:
        version = match.group(1)
        return version
    else:
        raise Exception("Could not find dagger version in output: " + version_output)


def check_dagger_cli_install() -> str:
    expected_dagger_cli_version = get_current_dagger_sdk_version()
    dagger_path = get_dagger_path()
    if dagger_path is None:
        LOGGER.info(f"The Dagger CLI is not installed. Installing {expected_dagger_cli_version}...")
        install_dagger_cli(expected_dagger_cli_version)
        dagger_path = get_dagger_path()

    cli_version = get_dagger_cli_version(dagger_path)
    if cli_version != expected_dagger_cli_version:
        LOGGER.warning(
            f"The Dagger CLI version '{cli_version}' does not match the expected version '{expected_dagger_cli_version}'. Installing Dagger CLI '{expected_dagger_cli_version}'..."
        )
        install_dagger_cli(expected_dagger_cli_version)
        return check_dagger_cli_install()
    return dagger_path


def main():
    os.environ[DAGGER_CLOUD_TOKEN_ENV_VAR_NAME_VALUE[0]] = DAGGER_CLOUD_TOKEN_ENV_VAR_NAME_VALUE[1]
    exit_code = 0
    if len(sys.argv) > 1 and any([arg in ARGS_DISABLING_TUI for arg in sys.argv]):
        command = ["airbyte-ci-internal"] + [arg for arg in sys.argv[1:] if arg != "--no-tui"]
    else:
        dagger_path = check_dagger_cli_install()
        command = [dagger_path, "run", "airbyte-ci-internal"] + sys.argv[1:]
    try:
        try:
            subprocess.run(command, check=True)
        except KeyboardInterrupt:
            LOGGER.info("Keyboard interrupt detected. Exiting...")
            exit_code = 1
    except subprocess.CalledProcessError as e:
        exit_code = e.returncode
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
