#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import io

import docker
import pytest


def build_docker_image(text: str, tag: str) -> docker.models.images.Image:
    """
    Really for this test we dont need to remove the image since we access it by a string name
    and remove it also by a string name. But maybe we wanna use it somewhere
    """
    client = docker.from_env()
    fileobj = io.BytesIO(bytes(text, "utf-8"))
    image, _ = client.images.build(fileobj=fileobj, tag=tag, forcerm=True, rm=True)
    return image


@pytest.fixture
def correct_connector_image() -> str:
    dockerfile_text = """
        FROM scratch
        ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
        ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]
        """
    tag = "my-valid-one"
    build_docker_image(dockerfile_text, tag)
    yield tag
    client = docker.from_env()
    client.images.remove(image=tag, force=True)


@pytest.fixture
def connector_image_without_env():
    dockerfile_text = """
        FROM scratch
        ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]
        """
    tag = "my-no-env"
    build_docker_image(dockerfile_text, tag)
    yield tag
    client = docker.from_env()
    client.images.remove(image=tag, force=True)


@pytest.fixture
def connector_image_with_ne_properties():
    dockerfile_text = """
        FROM scratch
        ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
        ENTRYPOINT ["python3", "/airbyte/integration_code/main.py"]
        """
    tag = "my-ne-properties"
    build_docker_image(dockerfile_text, tag)
    yield tag
    client = docker.from_env()
    client.images.remove(image=tag, force=True)
