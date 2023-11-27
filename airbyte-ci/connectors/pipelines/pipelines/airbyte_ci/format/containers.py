#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, List, Optional

import dagger
from pipelines.airbyte_ci.format.consts import DEFAULT_FORMAT_IGNORE_LIST
from pipelines.consts import AMAZONCORRETTO_IMAGE, GO_IMAGE, NODE_IMAGE, PYTHON_3_10_IMAGE
from pipelines.helpers.utils import sh_dash_c


def build_container(
    dagger_client: dagger.Client,
    base_image: str,
    include: List[str],
    install_commands: Optional[List[str]] = None,
    env_vars: Optional[Dict[str, Any]] = {},
) -> dagger.Container:
    """Build a container for formatting code.
    Args:
        ctx (ClickPipelineContext): The context of the pipeline
        base_image (str): The base image to use for the container
        include (List[str]): The list of files to include in the container
        install_commands (Optional[List[str]]): The list of commands to run to install dependencies for the formatter
        env_vars (Optional[Dict[str, Any]]): The list of environment variables to set on the container
    Returns:
        dagger.Container: The container to use for formatting
    """
    # Create container from base image
    container = dagger_client.container().from_(base_image)

    # Add any environment variables
    for key, value in env_vars.items():
        container = container.with_env_variable(key, value)

    # Install any dependencies of the formatter
    if install_commands:
        container = container.with_exec(sh_dash_c(install_commands), skip_entrypoint=True)

    # Mount the relevant parts of the repository: the code to format and the formatting config
    # Exclude the default ignore list to keep things as small as possible
    container = container.with_mounted_directory(
        "/src",
        dagger_client.host().directory(
            ".",
            include=include,
            exclude=DEFAULT_FORMAT_IGNORE_LIST,
        ),
    )

    # Set the working directory to the code to format
    container = container.with_workdir("/src")

    return container


def format_java_container(dagger_client: dagger.Client) -> dagger.Container:
    """Format java, groovy, and sql code via spotless."""
    return build_container(
        dagger_client,
        base_image=AMAZONCORRETTO_IMAGE,
        include=[
            "**/*.java",
            "**/*.gradle",
            "gradlew",
            "gradlew.bat",
            "gradle",
            "**/deps.toml",
            "**/gradle.properties",
            "**/version.properties",
            "tools/gradle/codestyle/java-google-style.xml",
        ],
        install_commands=[
            "yum update -y",
            "yum install -y findutils",  # gradle requires xargs, which is shipped in findutils.
            "yum clean all",
        ],
    )


def format_js_container(dagger_client: dagger.Client) -> dagger.Container:
    """Format yaml and json code via prettier."""
    return build_container(
        dagger_client,
        base_image=NODE_IMAGE,
        include=["**/*.yaml", "**/*.yml", "**.*/json", "package.json", "package-lock.json"],
        install_commands=["npm install -g npm@10.1.0 prettier@3.0.3"],
    )


def format_license_container(dagger_client: dagger.Client, license_file: str) -> dagger.Container:
    return build_container(
        dagger_client,
        base_image=GO_IMAGE,
        include=["**/*.java", "**/*.py", license_file],
        install_commands=["go get -u github.com/google/addlicense"],
    )


def format_python_container(dagger_client: dagger.Client) -> dagger.Container:
    """Format python code via black and isort."""

    return build_container(
        dagger_client,
        base_image=PYTHON_3_10_IMAGE,
        env_vars={"PIPX_BIN_DIR": "/usr/local/bin"},
        include=["**/*.py", "pyproject.toml", "poetry.lock"],
        install_commands=["pip install pipx", "pipx ensurepath", "pipx install poetry"],
    )
