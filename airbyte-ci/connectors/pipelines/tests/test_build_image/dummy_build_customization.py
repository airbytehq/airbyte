#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dagger import Container


async def pre_connector_install(base_image_container: Container) -> Container:
    """This function will run before the connector installation.
    It can mutate the base image container.

    Args:
        base_image_container (Container): The base image container to mutate.

    Returns:
        Container: The mutated base image container.
    """
    return base_image_container.with_env_variable("MY_PRE_BUILD_ENV_VAR", "my_pre_build_env_var_value")


async def post_connector_install(connector_container: Container) -> Container:
    """This function will run after the connector installation during the build process.
    It can mutate the connector container.

    Args:
        connector_container (Container): The connector container to mutate.

    Returns:
        Container: The mutated connector container.
    """
    return connector_container.with_env_variable("MY_POST_BUILD_ENV_VAR", "my_post_build_env_var_value")
