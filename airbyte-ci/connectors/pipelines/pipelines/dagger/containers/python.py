#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from dagger import CacheSharingMode, CacheVolume, Client, Container

from pipelines.airbyte_ci.connectors.context import PipelineContext
from pipelines.consts import (
    CONNECTOR_TESTING_REQUIREMENTS,
    PIP_CACHE_PATH,
    PIP_CACHE_VOLUME_NAME,
    POETRY_CACHE_PATH,
    POETRY_CACHE_VOLUME_NAME,
    PYPROJECT_TOML_FILE_PATH,
)
from pipelines.helpers.utils import sh_dash_c


def with_python_base(context: PipelineContext, python_version: str = "3.11") -> Container:
    """Build a Python container with a cache volume for pip cache.

    Args:
        context (PipelineContext): The current test context, providing a dagger client and a repository directory.
        python_image_name (str, optional): The python image to use to build the python base environment. Defaults to "python:3.9-slim".

    Raises:
        ValueError: Raised if the python_image_name is not a python image.

    Returns:
        Container: The python base environment container.
    """

    pip_cache: CacheVolume = context.dagger_client.cache_volume("pip_cache")

    base_container = (
        context.dagger_client.container()
        .from_(f"python:{python_version}-slim")
        .with_mounted_cache("/root/.cache/pip", pip_cache)
        .with_exec(
            sh_dash_c(
                [
                    "apt-get update",
                    "apt-get install -y build-essential cmake g++ libffi-dev libstdc++6 git",
                    "pip install pip==23.1.2",
                ]
            )
        )
    )

    return base_container


def with_testing_dependencies(context: PipelineContext) -> Container:
    """Build a testing environment by installing testing dependencies on top of a python base environment.

    Args:
        context (PipelineContext): The current test context, providing a dagger client and a repository directory.

    Returns:
        Container: The testing environment container.
    """
    python_environment: Container = with_python_base(context)
    pyproject_toml_file = context.get_repo_dir(".", include=[PYPROJECT_TOML_FILE_PATH]).file(PYPROJECT_TOML_FILE_PATH)

    return python_environment.with_exec(["pip", "install"] + CONNECTOR_TESTING_REQUIREMENTS).with_file(
        f"/{PYPROJECT_TOML_FILE_PATH}", pyproject_toml_file
    )


def with_pip_cache(container: Container, dagger_client: Client, owner: str | None = None) -> Container:
    """Mounts the pip cache in the container.
    Args:
        container (Container): A container with python installed
        owner (str, optional): The owner of the cache. Defaults to None.
    Returns:
        Container: A container with the pip cache mounted.
    """
    pip_cache_volume = dagger_client.cache_volume(PIP_CACHE_VOLUME_NAME)
    return container.with_mounted_cache(PIP_CACHE_PATH, pip_cache_volume, sharing=CacheSharingMode.SHARED, owner=owner)


def with_poetry_cache(container: Container, dagger_client: Client, owner: str | None = None) -> Container:
    """Mounts the poetry cache in the container.
    Args:
        container (Container): A container with python installed
        owner (str, optional): The owner of the cache. Defaults to None.
    Returns:
        Container: A container with the poetry cache mounted.
    """
    poetry_cache_volume = dagger_client.cache_volume(POETRY_CACHE_VOLUME_NAME)
    return container.with_mounted_cache(POETRY_CACHE_PATH, poetry_cache_volume, sharing=CacheSharingMode.SHARED, owner=owner)
