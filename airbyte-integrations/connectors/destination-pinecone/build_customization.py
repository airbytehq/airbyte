#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from dagger import Container


async def pre_connector_install(base_image_container: Container) -> Container:
    """
    Docker compose is required to run the integration tests so we install Docker on top of the base image.
    """
    return base_image_container.with_exec(["sh", "-c", "apt-get update && apt-get install -y build-essential gcc"], use_entrypoint=True)
