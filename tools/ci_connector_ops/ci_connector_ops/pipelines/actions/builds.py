#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import tempfile
from typing import List, Optional, Tuple

import docker
from ci_connector_ops.pipelines.contexts import ConnectorTestContext


async def build_dev_image(context: ConnectorTestContext, exclude: Optional[List] = None) -> Tuple[str, str]:
    """Build the connector docker image and tag it with dev.

    Args:
        context (ConnectorTestContext): The current test context, providing a dagger client, a connector object and a repository directory.
        exclude (List, optional): The list of directory or file that should not be considered in the image build. Defaults to None.

    Raises:
        Exception: Raised if an error happened during image build.
        Exception: Raised if an error happened during image tagging.

    Returns:
        Tuple[str, str]: The built image name and tag, the built image short id.
    """
    local_image_tarball_path = tempfile.NamedTemporaryFile()
    local_docker_client = docker.from_env()
    dev_tag = context.connector.definition["dockerRepository"].split(":")[0] + ":dev"
    exported = await (context.get_connector_dir(exclude=exclude).docker_build().export(local_image_tarball_path.name))

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
