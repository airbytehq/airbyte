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
    current_user = (await base_image_container.with_exec(["whoami"]).stdout()).strip()
    return (
        base_image_container.with_user("root")
        .with_exec(["mkdir", "/config"])
        .with_exec(["chown", f"{current_user}:{current_user}", "/config"])
        .with_user(current_user)
    )
