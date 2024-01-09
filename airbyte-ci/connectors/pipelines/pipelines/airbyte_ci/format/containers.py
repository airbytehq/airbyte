#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, List, Optional

import dagger
from pipelines.airbyte_ci.format.consts import CACHE_MOUNT_PATH, DEFAULT_FORMAT_IGNORE_LIST, REPO_MOUNT_PATH, WARM_UP_INCLUSIONS, Formatter
from pipelines.consts import GO_IMAGE, MAVEN_IMAGE, NODE_IMAGE, PYTHON_3_10_IMAGE
from pipelines.helpers import cache_keys
from pipelines.helpers.utils import sh_dash_c


def build_container(
    dagger_client: dagger.Client,
    base_image: str,
    dir_to_format: dagger.Directory,
    warmup_dir: Optional[dagger.Directory] = None,
    install_commands: Optional[List[str]] = None,
    env_vars: Dict[str, Any] = {},
    cache_volume: Optional[dagger.CacheVolume] = None,
) -> dagger.Container:
    """Build a container for formatting code.
    Args:
        ctx (ClickPipelineContext): The context of the pipeline
        base_image (str): The base image to use for the container
        dir_to_format (Directory): A directory with the source code to format
        warmup_dir (Optional[Directory], optional): A directory with the source code to warm up the container cache. Defaults to None.
        install_commands (Optional[List[str]], optional): A list of commands to run to install dependencies. Defaults to None.
        env_vars (Optional[Dict[str, Any]], optional): A dictionary of environment variables to set in the container. Defaults to {}.
        cache_volume (Optional[CacheVolume], optional): A cache volume to mount in the container. Defaults to None.

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
    if warmup_dir:
        container = container.with_mounted_directory(
            REPO_MOUNT_PATH,
            warmup_dir,
        )

    # Install any dependencies of the formatter
    if install_commands:
        container = container.with_exec(sh_dash_c(install_commands), skip_entrypoint=True)

    # Mount the relevant parts of the repository: the code to format and the formatting config
    # Exclude the default ignore list to keep things as small as possible.
    # The mount path is the same as for the earlier volume mount, this will cause those directory
    # contents to be overwritten. This is intentional and not a concern as the current file set is
    # a superset of the earlier one.
    if warmup_dir:
        container = container.with_mounted_directory(REPO_MOUNT_PATH, dir_to_format.with_directory(".", warmup_dir))
    else:
        container = container.with_mounted_directory(REPO_MOUNT_PATH, dir_to_format)
    if cache_volume:
        container = container.with_mounted_cache(CACHE_MOUNT_PATH, cache_volume)
    return container


def format_java_container(dagger_client: dagger.Client, java_code: dagger.Directory) -> dagger.Container:
    """
    Create a Maven container with spotless installed with mounted code to format and a cache volume.
    We warm up the container cache with the spotless configuration and dependencies.
    """
    warmup_dir = dagger_client.host().directory(
        ".",
        include=WARM_UP_INCLUSIONS[Formatter.JAVA],
        exclude=DEFAULT_FORMAT_IGNORE_LIST,
    )
    return build_container(
        dagger_client,
        base_image=MAVEN_IMAGE,
        warmup_dir=warmup_dir,
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
        dir_to_format=java_code,
    )


def format_js_container(dagger_client: dagger.Client, js_code: dagger.Directory, prettier_version: str = "3.0.3") -> dagger.Container:
    """Create a Node container with prettier installed with mounted code to format and a cache volume."""
    return build_container(
        dagger_client,
        base_image=NODE_IMAGE,
        dir_to_format=js_code,
        install_commands=[f"npm install -g npm@10.1.0 prettier@{prettier_version}"],
        cache_volume=dagger_client.cache_volume(cache_keys.get_prettier_cache_key(prettier_version)),
    )


def format_license_container(dagger_client: dagger.Client, license_code: dagger.Directory) -> dagger.Container:
    """Create a Go container with addlicense installed with mounted code to format."""
    warmup_dir = dagger_client.host().directory(".", include=WARM_UP_INCLUSIONS[Formatter.LICENSE], exclude=DEFAULT_FORMAT_IGNORE_LIST)
    return build_container(
        dagger_client,
        base_image=GO_IMAGE,
        dir_to_format=license_code,
        install_commands=["go get -u github.com/google/addlicense"],
        warmup_dir=warmup_dir,
    )


def format_python_container(
    dagger_client: dagger.Client, python_code: dagger.Directory, black_version: str = "~22.3.0"
) -> dagger.Container:
    """Create a Python container with pipx and the global pyproject.toml installed with mounted code to format and a cache volume.
    We warm up the container with the pyproject.toml and poetry.lock files to not repeat the pyproject.toml installation.
    """

    warmup_dir = dagger_client.host().directory(".", include=WARM_UP_INCLUSIONS[Formatter.PYTHON], exclude=DEFAULT_FORMAT_IGNORE_LIST)
    return build_container(
        dagger_client,
        base_image=PYTHON_3_10_IMAGE,
        env_vars={"PIPX_BIN_DIR": "/usr/local/bin", "BLACK_CACHE_DIR": f"{CACHE_MOUNT_PATH}/black"},
        install_commands=[
            "pip install pipx",
            "pipx ensurepath",
            "pipx install poetry",
            "poetry install --no-root",
        ],
        dir_to_format=python_code,
        warmup_dir=warmup_dir,
        # Namespacing the cache volume by black version is likely overkill:
        # Black already manages cache directories by version internally.
        # https://github.com/psf/black/blob/e4ae213f06050e7f76ebcf01578c002e412dafdc/src/black/cache.py#L42
        cache_volume=dagger_client.cache_volume(cache_keys.get_black_cache_key(black_version)),
    )
