# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Image build customization script.

Docker compose is required to run the integration tests so we install Docker on top of the base
image.
"""

from __future__ import annotations

from contextlib import suppress
from types import ModuleType
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    dagger: ModuleType | None = None
    with suppress(ImportError):
        from dagger import Container


async def pre_connector_install(base_image_container: Container) -> Container:
    return (
        base_image_container.with_exec(["sh", "-c", "apt-get update && apt-get install -y curl jq"], use_entrypoint=True)
        .with_exec(["curl", "-fsSL", "https://get.docker.com", "-o", "/tmp/install-docker.sh"], use_entrypoint=True)
        .with_exec(["sh", "/tmp/install-docker.sh", "--version", "25.0"], use_entrypoint=True)
        .with_exec(["rm", "/tmp/install-docker.sh"], use_entrypoint=True)
    )


if __name__ == "__main__":
    # If this script is invoked directly, run the steps directly using the subprocess module.
    # This is useful for running the script outside of a Dagger environment.
    import subprocess

    subprocess.run(["sh", "-c", "apt-get update && apt-get install -y curl jq"], check=True)
    subprocess.run(["curl", "-fsSL", "https://get.docker.com", "-o", "/tmp/install-docker.sh"], check=True)
    subprocess.run(["sh", "/tmp/install-docker.sh", "--version", "25.0"], check=True)
    subprocess.run(["rm", "/tmp/install-docker.sh"], check=True)
