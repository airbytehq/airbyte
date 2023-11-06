# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


def with_go(context: PipelineContext, go_version: str = "3.10") -> Container:
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
