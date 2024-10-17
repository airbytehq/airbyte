#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re
from typing import Optional

import dagger
from base_images import errors


async def check_env_var_with_printenv(
    container: dagger.Container, expected_env_var_name: str, expected_env_var_value: Optional[str] = None
):
    """This checks if an environment variable is correctly defined by calling the printenv command in a container.

    Args:
        container (dagger.Container): The container on which the sanity checks should run.
        expected_env_var_name (str): The name of the environment variable to check.
        expected_env_var_value (Optional[str], optional): The expected value of the environment variable. Defaults to None.

    Raises:
        errors.SanityCheckError: Raised if the environment variable is not defined or if it has an unexpected value.
    """
    try:
        printenv_output = await container.with_exec(["printenv"]).stdout()
    except dagger.ExecError as e:
        raise errors.SanityCheckError(e)
    env_vars = {line.split("=")[0]: line.split("=")[1] for line in printenv_output.splitlines()}
    if expected_env_var_name not in env_vars:
        raise errors.SanityCheckError(f"the {expected_env_var_name} environment variable is not defined.")
    if expected_env_var_value is not None and env_vars[expected_env_var_name] != expected_env_var_value:
        raise errors.SanityCheckError(
            f"the {expected_env_var_name} environment variable is defined but has an unexpected value: {env_vars[expected_env_var_name]}."
        )


async def check_timezone_is_utc(container: dagger.Container):
    """Check that the system timezone is UTC.

    Args:
        container (dagger.Container): The container on which the sanity checks should run.

    Raises:
        errors.SanityCheckError: Raised if the date command could not be executed or if the outputted timezone is not UTC.
    """
    try:
        tz_output: str = await container.with_exec(["date"]).stdout()
    except dagger.ExecError as e:
        raise errors.SanityCheckError(e)
    if "UTC" not in tz_output:
        raise errors.SanityCheckError(f"unexpected timezone: {tz_output}")


async def check_a_command_is_available_using_version_option(container: dagger.Container, command: str, version_option: str = "--version"):
    """Checks that a command is available in the container by calling it with the --version option.

    Args:
        container (dagger.Container): The container on which the sanity checks should run.
        command (str): The command to check.

    Raises:
        errors.SanityCheckError: Raised if the command could not be executed or if the outputted version is not the expected one.
    """
    try:
        command_version_output: str = await container.with_exec([command, version_option]).stdout()
    except dagger.ExecError as e:
        raise errors.SanityCheckError(e)
    if command_version_output == "":
        raise errors.SanityCheckError(f"unexpected {command} version: {command_version_output}")


async def check_socat_version(container: dagger.Container, expected_socat_version: str):
    """Checks that the socat version is the expected one.

    Args:
        container (dagger.Container): The container on which the sanity checks should run.
        expected_socat_version (str): The expected socat version.

    Raises:
        errors.SanityCheckError: Raised if the socat --version command could not be executed or if the outputted version is not the expected one.
    """
    try:
        socat_version_output: str = await container.with_exec(["socat", "-V"]).stdout()
    except dagger.ExecError as e:
        raise errors.SanityCheckError(e)
    socat_version_line = None
    for line in socat_version_output.splitlines():
        if line.startswith("socat version"):
            socat_version_line = line
            break
    if socat_version_line is None:
        raise errors.SanityCheckError(f"Could not parse the socat version from the output: {socat_version_output}")
    version_pattern = r"version (\d+\.\d+\.\d+\.\d+)"
    match = re.search(version_pattern, socat_version_line)
    if match:
        version_number = match.group(1)
        if version_number != expected_socat_version:
            raise errors.SanityCheckError(f"unexpected socat version: {version_number}")
    else:
        raise errors.SanityCheckError(f"Could not find the socat version in the version output: {socat_version_line}")
