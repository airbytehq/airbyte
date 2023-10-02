#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import dagger
from base_images import errors
from base_images import sanity_checks as base_sanity_checks


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


async def check_python_image_has_expected_env_vars(python_image_container: dagger.Container):
    """Check a python container has the set of env var we always expect on python images.

    Args:
        python_image_container (dagger.Container): The container on which the sanity checks should run.
    """
    expected_env_vars = {
        "PYTHON_VERSION",
        "PYTHON_PIP_VERSION",
        "PYTHON_GET_PIP_SHA256",
        "PYTHON_GET_PIP_URL",
        "HOME",
        "PATH",
        "LANG",
        "GPG_KEY",
        "OTEL_EXPORTER_OTLP_TRACES_PROTOCOL",
        "PYTHON_SETUPTOOLS_VERSION",
        "OTEL_TRACES_EXPORTER",
        "OTEL_TRACE_PARENT",
        "TRACEPARENT",
    }
    # It's not suboptimal to call printenv multiple times because the printenv output is cached.
    for expected_env_var in expected_env_vars:
        await base_sanity_checks.check_env_var_with_printenv(python_image_container, expected_env_var)
