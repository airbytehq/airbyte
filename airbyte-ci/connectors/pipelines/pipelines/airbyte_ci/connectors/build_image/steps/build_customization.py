#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import importlib
from logging import Logger
from types import ModuleType
from typing import List, Optional

from connector_ops.utils import Connector  # type: ignore
from dagger import Container

BUILD_CUSTOMIZATION_MODULE_NAME = "build_customization"
BUILD_CUSTOMIZATION_SPEC_NAME = f"{BUILD_CUSTOMIZATION_MODULE_NAME}.py"
DEFAULT_MAIN_FILE_NAME = "main.py"


def get_build_customization_module(connector: Connector) -> Optional[ModuleType]:
    """Import the build_customization.py file from the connector directory if it exists.
    Returns:
        Optional[ModuleType]: The build_customization.py module if it exists, None otherwise.
    """
    build_customization_spec_path = connector.code_directory / BUILD_CUSTOMIZATION_SPEC_NAME

    if not build_customization_spec_path.exists() or not (
        build_customization_spec := importlib.util.spec_from_file_location(
            f"{connector.code_directory.name}_{BUILD_CUSTOMIZATION_MODULE_NAME}", build_customization_spec_path
        )
    ):
        return None

    if build_customization_spec.loader is None:
        return None

    build_customization_module = importlib.util.module_from_spec(build_customization_spec)
    build_customization_spec.loader.exec_module(build_customization_module)
    return build_customization_module


def get_main_file_name(connector: Connector) -> str:
    """Get the main file name from the build_customization.py module if it exists, DEFAULT_MAIN_FILE_NAME otherwise.

    Args:
        connector (Connector): The connector to build.

    Returns:
        str: The main file name.
    """
    build_customization_module = get_build_customization_module(connector)

    return (
        build_customization_module.MAIN_FILE_NAME
        if build_customization_module and hasattr(build_customization_module, "MAIN_FILE_NAME")
        else DEFAULT_MAIN_FILE_NAME
    )


def get_entrypoint(connector: Connector) -> List[str]:
    main_file_name = get_main_file_name(connector)
    return ["python", f"/airbyte/integration_code/{main_file_name}"]


def apply_airbyte_entrypoint(connector_container: Container, connector: Connector) -> Container:
    entrypoint = get_entrypoint(connector)

    return connector_container.with_env_variable("AIRBYTE_ENTRYPOINT", " ".join(entrypoint)).with_entrypoint(entrypoint)


async def pre_install_hooks(connector: Connector, base_container: Container, logger: Logger) -> Container:
    """Run the pre_connector_install hook if it exists in the build_customization.py module.
    It will mutate the base_container and return it.

    Args:
        connector (Connector): The connector to build.
        base_container (Container): The base container to mutate.
        logger (Logger): The logger to use.

    Returns:
        Container: The mutated base_container.
    """
    build_customization_module = get_build_customization_module(connector)
    if build_customization_module and hasattr(build_customization_module, "pre_connector_install"):
        base_container = await build_customization_module.pre_connector_install(base_container)
        logger.info(f"Connector {connector.technical_name} pre install hook executed.")
    return base_container


async def post_install_hooks(connector: Connector, connector_container: Container, logger: Logger) -> Container:
    """Run the post_connector_install hook if it exists in the build_customization.py module.
    It will mutate the connector_container and return it.

    Args:
        connector (Connector): The connector to build.
        connector_container (Container): The connector container to mutate.
        logger (Logger): The logger to use.

    Returns:
        Container: The mutated connector_container.
    """
    build_customization_module = get_build_customization_module(connector)
    if build_customization_module and hasattr(build_customization_module, "post_connector_install"):
        connector_container = await build_customization_module.post_connector_install(connector_container)
        logger.info(f"Connector {connector.technical_name} post install hook executed.")
    return connector_container
