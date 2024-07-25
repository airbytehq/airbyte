#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dagger import Container


async def pre_connector_install(base_image_container: Container) -> Container:
    """This function will run before the connector installation.
    We set these environment variable to match what was originally in the Dockerfile.
    Disclaimer: I have no idea if these env vars are actually needed.
    """
    return base_image_container.with_env_variable("AIRBYTE_IMPL_MODULE", "source_zendesk_chat").with_env_variable(
        "AIRBYTE_IMPL_PATH", "SourceZendeskChat"
    )
