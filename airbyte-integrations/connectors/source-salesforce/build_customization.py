from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dagger import Container


async def pre_connector_install(base_image_container: Container) -> Container:
    """
    This function will run before the connector installation.
    This function sets PROXY environment variables of the docker image.
    The value for Proxy variables may change depending on the environment(staging or prod),
    so we read its value from environment.
    """
    HTTP_PROXY = os.environ["IMAGE_HTTP_PROXY"]
    HTTPS_PROXY = os.environ["IMAGE_HTTPS_PROXY"]

    return await base_image_container.with_env_variable("HTTP_PROXY", HTTP_PROXY).with_env_variable("HTTPS_PROXY", HTTPS_PROXY)