#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from gql.transport.exceptions import TransportQueryError

PYPROJECT_TOML_FILE_PATH = "pyproject.toml"

INSTALL_LOCAL_REQUIREMENTS_CMD = ["python", "-m", "pip", "install", "-r", "requirements.txt"]
INSTALL_REQUIREMENTS_CMD = ["python", "-m", "pip", "install", "."]


async def install_requirements(client, connector_builder, extras=None):
    try:
        requirement_file_exists = await connector_builder.file("requirements.txt").size() > 0
    except TransportQueryError:
        requirement_file_exists = False

    if requirement_file_exists:
        connector_builder = connector_builder.with_exec(INSTALL_LOCAL_REQUIREMENTS_CMD)
    connector_builder = connector_builder.with_exec(INSTALL_REQUIREMENTS_CMD)

    if extras:
        connector_builder = connector_builder.with_exec(
            INSTALL_REQUIREMENTS_CMD[:-1] + [INSTALL_REQUIREMENTS_CMD[-1] + f"[{','.join(extras)}]"]
        )

    return await connector_builder.exit_code()
