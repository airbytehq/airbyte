#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, List, Optional

import dagger
from pipelines.airbyte_ci.format.consts import DEFAULT_FORMAT_IGNORE_LIST, REPO_MOUNT_PATH
from pipelines.consts import GO_IMAGE, MAVEN_IMAGE, NODE_IMAGE, PYTHON_3_10_IMAGE
from pipelines.helpers.utils import sh_dash_c


def build_container(
    dagger_client: dagger.Client,
    base_image: str,
    include: List[str],
    warmup_include: Optional[List[str]] = None,
    install_commands: Optional[List[str]] = None,
    env_vars: Optional[Dict[str, Any]] = {},
) -> dagger.Container:
    """Build a container for formatting code.
    Args:
        ctx (ClickPipelineContext): The context of the pipeline
        base_image (str): The base image to use for the container
        include (List[str]): The list of files to include in the container
        warmup_include (Optional[List[str]]): The list of files to include in the container before installing dependencies
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

    # Set the working directory to the code to format
    container = container.with_workdir(REPO_MOUNT_PATH)

    # Mount files to be referenced by the install_commands, if requested.
    # These should only be files which do not change very often, to avoid invalidating the layer cache.
    if warmup_include:
        container = container.with_mounted_directory(
            REPO_MOUNT_PATH,
            dagger_client.host().directory(
                ".",
                include=warmup_include,
                exclude=DEFAULT_FORMAT_IGNORE_LIST,
            ),
        )

    # Install any dependencies of the formatter
    if install_commands:
        container = container.with_exec(sh_dash_c(install_commands), skip_entrypoint=True)

    # Mount the relevant parts of the repository: the code to format and the formatting config
    # Exclude the default ignore list to keep things as small as possible.
    # The mount path is the same as for the earlier volume mount, this will cause those directory
    # contents to be overwritten. This is intentional and not a concern as the current file set is
    # a superset of the earlier one.
    container = container.with_mounted_directory(
        REPO_MOUNT_PATH,
        dagger_client.host().directory(
            ".",
            include=include + (warmup_include if warmup_include else []),
            exclude=DEFAULT_FORMAT_IGNORE_LIST,
        ),
    )

    return container


def format_java_container(dagger_client: dagger.Client) -> dagger.Container:
    """
    Format java and groovy code via spotless in maven.
    We use maven instead of gradle because we want this formatting step to be fast.
    """
    return build_container(
        dagger_client,
        base_image=MAVEN_IMAGE,
        warmup_include=[
            "spotless-maven-pom.xml",
            "tools/gradle/codestyle/java-google-style.xml",
        ],
        install_commands=[
            # Run maven before mounting the sources to download all its dependencies.
            # Dagger will cache the resulting layer to minimize the downloads.
            # The go-offline goal purportedly downloads all dependencies.
            # This isn't quite the case, we still need to add spotless goals.
            "mvn -f spotless-maven-pom.xml"
            " org.apache.maven.plugins:maven-dependency-plugin:3.6.1:go-offline"
            " spotless:apply"
            " spotless:check"
            " clean"
        ],
        include=["**/*.java", "**/*.gradle"],
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
        warmup_include=["pyproject.toml", "poetry.lock"],
        install_commands=[
            "pip install pipx",
            "pipx ensurepath",
            "pipx install poetry",
            "poetry install --no-root",
        ],
        include=["**/*.py"],
    )
