# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dagger import Container


async def pre_connector_install(base_image_container: Container) -> Container:
    """
    Docker compose is required to run the integration tests so we install Docker on top of the base image.
    """
    return (
        base_image_container.with_exec(["sh", "-c", "apt-get update && apt-get install -y curl jq"])
        # Download install-docker.sh script
        .with_exec(["curl", "-fsSL", "https://get.docker.com", "-o", "/tmp/install-docker.sh"])
        # Run the install-docker.sh script with a pinned Docker version
        .with_exec(["sh", "/tmp/install-docker.sh", "--version", "25.0"])
        # Remove the install-docker.sh script
        .with_exec(["rm", "/tmp/install-docker.sh"])
    )
