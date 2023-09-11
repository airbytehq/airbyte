#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import Optional

import dagger
from base_images import errors


async def check_env_var_defined_with_dagger(
    container: dagger.Container, expected_env_var_name: str, expected_env_var_value: Optional[str] = None
):
    """This checks if an environment variable is correctly defined with dagger.
    This is a better check than the one using printenv in some contexts were we have no guarantee that the printenv command is available.

    Args:
        container (dagger.Container): The container on which the sanity checks should run.
        expected_env_var_name (str): The name of the environment variable to check.
        expected_env_var_value (Optional[str], optional): The expected value of the environment variable. Defaults to None.

    Raises:
        errors.SanityCheckError: Raised if the environment variable is not defined or if it has an unexpected value.
    """
    env_var_value = await container.env_variable(expected_env_var_name)
    if env_var_value is None:
        raise errors.SanityCheckError(f"the {expected_env_var_name} environment variable is not defined.")
    if expected_env_var_value is not None and env_var_value != expected_env_var_value:
        raise errors.SanityCheckError(
            f"the {expected_env_var_name} environment variable is defined but has an unexpected value: {env_var_value}."
        )


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
        printenv_output = await container.with_exec(["printenv"], skip_entrypoint=True).stdout()
    except dagger.ExecError as e:
        raise errors.SanityCheckError(e)
    env_vars = {line.split("=")[0]: line.split("=")[1] for line in printenv_output.splitlines()}
    if expected_env_var_name not in env_vars:
        raise errors.SanityCheckError(f"the {expected_env_var_name} environment variable is not defined.")
    if expected_env_var_value is not None and env_vars[expected_env_var_name] != expected_env_var_value:
        raise errors.SanityCheckError(
            f"the {expected_env_var_name} environment variable is defined but has an unexpected value: {env_vars[expected_env_var_name]}."
        )


async def check_label_defined_with_dagger(container: dagger.Container, expected_label: str, expected_label_value: Optional[str] = None):
    """This checks if a label is correctly defined with dagger.

    Args:
        container (dagger.Container): The container on which the sanity checks should run.
        expected_env_var_name (str): The name of the label to check.
        expected_env_var_value (Optional[str], optional): The expected value of the label. Defaults to None.

    Raises:
        errors.SanityCheckError: Raised if the environment variable is not defined or if it has an unexpected value.
    """
    label_value = await container.label(expected_label)
    if label_value is None:
        raise errors.SanityCheckError(f"the {expected_label_value} label is not defined.")
    if expected_label_value is not None and label_value != expected_label_value:
        raise errors.SanityCheckError(f"the {expected_label_value} label is defined but has an unexpected value: {label_value}.")


async def check_timezone_is_utc(container: dagger.Container):
    """Check that the system timezone is UTC.

    Args:
        container (dagger.Container): The container on which the sanity checks should run.

    Raises:
        errors.SanityCheckError: Raised if the date command could not be executed or if the outputted timezone is not UTC.
    """
    try:
        tz_output: str = await container.with_exec(["date"], skip_entrypoint=True).stdout()
    except dagger.ExecError as e:
        raise errors.SanityCheckError(e)
    if "UTC" not in tz_output:
        raise errors.SanityCheckError(f"unexpected timezone: {tz_output}")


async def check_a_command_is_available_using_version_option(container: dagger.Container, command: str):
    """Checks that a command is available in the container by calling it with the --version option.

    Args:
        container (dagger.Container): The container on which the sanity checks should run.
        command (str): The command to check.

    Raises:
        errors.SanityCheckError: Raised if the command could not be executed or if the outputted version is not the expected one.
    """
    try:
        command_version_output: str = await container.with_exec([command, "--version"], skip_entrypoint=True).stdout()
    except dagger.ExecError as e:
        raise errors.SanityCheckError(e)
    if command_version_output == "":
        raise errors.SanityCheckError(f"unexpected {command} version: {command_version_output}")


async def check_python_version(container: dagger.Container, expected_python_version: str):
    """Checks that the python version is the expected one.

    Args:
        container (dagger.Container): The container on which the sanity checks should run.
        expected_python_version (str): The expected python version.

    Raises:
        errors.SanityCheckError: Raised if the python --version command could not be executed or if the outputted version is not the expected one.
    """
    try:
        python_version_output: str = await container.with_exec(["python", "--version"], skip_entrypoint=True).stdout()
    except dagger.ExecError as e:
        raise errors.SanityCheckError(e)
    if python_version_output != f"Python {expected_python_version}\n":
        raise errors.SanityCheckError(f"unexpected python version: {python_version_output}")


async def check_pip_version(container: dagger.Container, expected_pip_version: str):
    """Checks that the pip version is the expected one.

    Args:
        container (dagger.Container): The container on which the sanity checks should run.
        expected_pip_version (str): The expected pip version.

    Raises:
        errors.SanityCheckError: Raised if the pip --version command could not be executed or if the outputted version is not the expected one.
    """
    try:
        pip_version_output: str = await container.with_exec(["pip", "--version"], skip_entrypoint=True).stdout()
    except dagger.ExecError as e:
        raise errors.SanityCheckError(e)
    if not pip_version_output.startswith(f"pip {expected_pip_version}"):
        raise errors.SanityCheckError(f"unexpected pip version: {pip_version_output}")


async def check_poetry_version(container: dagger.Container, expected_poetry_version: str):
    """Checks that the poetry version is the expected one.

    Args:
        container (dagger.Container): The container on which the sanity checks should run.
        expected_poetry_version (str): The expected poetry version.

    Raises:
        errors.SanityCheckError: Raised if the poetry --version command could not be executed or if the outputted version is not the expected one.
    """
    try:
        poetry_version_output: str = await container.with_exec(["poetry", "--version"], skip_entrypoint=True).stdout()
    except dagger.ExecError as e:
        raise errors.SanityCheckError(e)
    if not poetry_version_output.startswith(f"Poetry (version {expected_poetry_version}"):
        raise errors.SanityCheckError(f"unexpected poetry version: {poetry_version_output}")
