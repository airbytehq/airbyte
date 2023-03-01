#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import tempfile
from typing import List, Optional, Tuple

import docker
from ci_connector_ops.utils import Connector
from dagger import Client


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
