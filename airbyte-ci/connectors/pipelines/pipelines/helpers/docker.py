# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from pipelines.consts import DOCKER_REGISTRY_INDEX


def get_image_name_with_registry_index(image_name: str, registry_index: str = DOCKER_REGISTRY_INDEX) -> str:
    """Prepend the registry index to the image name if it is not already present.

    Args:
        image_name (str): The image name to append the registry index to.
        registry_index (str, optional): The registry index host (e.g. docker.io, gcr.io). Defaults to DOCKER_REGISTRY_INDEX.

    Returns:
        str: The image name with the registry index prepended.
    """
    if len(image_name.split("/")) == 3 and "." in image_name.split("/")[0]:
        return image_name
    return f"{registry_index}/{image_name}"
