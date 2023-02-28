#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import tempfile
from typing import List, Optional, Tuple

import docker
from ci_connector_ops.pipelines.utils import check_path_in_workdir
from ci_connector_ops.utils import Connector
from dagger import Client, Container

INSTALL_LOCAL_REQUIREMENTS_CMD = ["python", "-m", "pip", "install", "-r", "requirements.txt"]
INSTALL_REQUIREMENTS_CMD = ["python", "-m", "pip", "install", "."]


async def install(dagger_client: Client, connector_container: Container, extras: Optional[List] = None) -> Container:
    """Create container in which the connector python package is installed with all its dependencies.

    Args:
        dagger_client (Client): _description_
        connector_container (Container): _description_
        extras (List, optional): List of extra_requires to intall e.g: tests, dev, main. (pip install -e .[tests]). Defaults to None.

    Returns:
        Container: A container in which the connector python package is installed with all its dependencies
    """
    if await check_path_in_workdir(connector_container, "requirements.txt"):
        requirements_txt = await connector_container.file("requirements.txt").contents()
        for line in requirements_txt.split("\n"):
            if line.startswith("-e ../../"):
                local_dependency_to_mount = line.replace("-e ../..", "airbyte-integrations")
                connector_container = connector_container.with_mounted_directory(
                    "/" + local_dependency_to_mount, dagger_client.host().directory(local_dependency_to_mount, exclude=[".venv"])
                )
        connector_container = connector_container.with_exec(INSTALL_LOCAL_REQUIREMENTS_CMD)
    connector_container = connector_container.with_exec(INSTALL_REQUIREMENTS_CMD)

    if extras:
        connector_container = connector_container.with_exec(
            INSTALL_REQUIREMENTS_CMD[:-1] + [INSTALL_REQUIREMENTS_CMD[-1] + f"[{','.join(extras)}]"]
        )

    return connector_container


async def build_dev_image(dagger_client: Client, connector: Connector, exclude=Optional[List]) -> Tuple[str, str]:
    """Build the connector docker image and tag it with dev.

    Args:
        dagger_client (Client): The dagger client.
        connector (Connector): The connector for which you want to build a dev image.
        exclude (List, optional): The list of directory or file that should not be considered in the image build. Defaults to Optional[List].

    Raises:
        Exception: Raised if an error happened during image build.
        Exception: Raised if an error happened during image tagging.

    Returns:
        Tuple[str, str]: The built image name and tag, the built image short id.
    """
    # Question to Dagger team: Can build and tag an image in Dagger?
    local_image_tarball_path = tempfile.NamedTemporaryFile()
    local_docker_client = docker.from_env()
    dev_tag = connector.definition["dockerRepository"].split(":")[0] + ":dev"
    exported = (
        await dagger_client.host()
        .directory(str(connector.code_directory), exclude=exclude)
        .docker_build()
        .export(local_image_tarball_path.name)
    )
    if exported:
        with open(local_image_tarball_path.name, "rb") as image_archive:
            connector_image = local_docker_client.images.load(image_archive.read())[0]
        tagged = connector_image.tag(dev_tag)
        if tagged:
            return dev_tag, connector_image.short_id
        else:
            raise Exception("The image could not be tagged.")
    else:
        raise Exception("The image could not be built.")
