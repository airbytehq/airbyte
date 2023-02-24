#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from ci_connector_ops.ci.utils import check_path_in_workdir
from dagger.api.gen import Container

INSTALL_LOCAL_REQUIREMENTS_CMD = ["python", "-m", "pip", "install", "-r", "requirements.txt"]
INSTALL_REQUIREMENTS_CMD = ["python", "-m", "pip", "install", "."]


async def install(client, connector_container: Container, extras=None):

    if await check_path_in_workdir(connector_container, "requirements.txt"):
        requirements_txt = connector_container.file("requirements.txt").contents()
        for line in requirements_txt.split("\n"):
            if line.startswith("-e ../../"):
                local_dependency_to_mount = line.replace("-e ../..", "airbyte-integrations")
                connector_container = connector_container.with_mounted_directory(
                    "/" + local_dependency_to_mount, client.host().directory(local_dependency_to_mount, exclude=[".venv"])
                )
        connector_container = connector_container.with_exec(INSTALL_LOCAL_REQUIREMENTS_CMD)
    connector_container = connector_container.with_exec(INSTALL_REQUIREMENTS_CMD)

    if extras:
        connector_container = connector_container.with_exec(
            INSTALL_REQUIREMENTS_CMD[:-1] + [INSTALL_REQUIREMENTS_CMD[-1] + f"[{','.join(extras)}]"]
        )

    return connector_container


# async def build_image(client, connector_name):
#     source_host_path = client.host().directory(
#         f"airbyte-integrations/connectors/{connector_name}", include=["Dockerfile", "main.py", "setup.py", connector_name.replace("-", "_")]
#     )
#     tag = f"airbyte/{connector_name}:dev"
#     ref = await source_host_path.docker_build().publish(tag)
#     return tag, ref
