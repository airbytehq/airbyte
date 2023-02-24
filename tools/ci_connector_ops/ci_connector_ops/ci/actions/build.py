#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from ci_connector_ops.ci.actions.connector_builder import connector_has_path

INSTALL_LOCAL_REQUIREMENTS_CMD = ["python", "-m", "pip", "install", "-r", "requirements.txt"]
INSTALL_REQUIREMENTS_CMD = ["python", "-m", "pip", "install", "."]


def get_connector_acceptance_test_source_mount_args(client):
    host_path = "airbyte-integrations/bases/connector-acceptance-test"
    return "/" + host_path, client.host().directory(host_path, exclude=[".venv"])


async def install_requirements(client, connector_builder, extras=None):
    connector_builder = connector_builder.with_mounted_directory(*get_connector_acceptance_test_source_mount_args(client))

    if await connector_has_path(connector_builder, "requirements.txt"):
        connector_builder = connector_builder.with_exec(INSTALL_LOCAL_REQUIREMENTS_CMD)
    connector_builder = connector_builder.with_exec(INSTALL_REQUIREMENTS_CMD)

    if extras:
        connector_builder = connector_builder.with_exec(
            INSTALL_REQUIREMENTS_CMD[:-1] + [INSTALL_REQUIREMENTS_CMD[-1] + f"[{','.join(extras)}]"]
        )

    return await connector_builder.exit_code(), connector_builder

async def build_image(client, connector_name):
    source_host_path = client.host().directory(
        f"airbyte-integrations/connectors/{connector_name}", include=["Dockerfile", "main.py", "setup.py", connector_name.replace("-", "_")]
    )
    tag = f"airbyte/{connector_name}:dev"
    ref = await source_host_path.docker_build().publish(tag)
    return tag, ref