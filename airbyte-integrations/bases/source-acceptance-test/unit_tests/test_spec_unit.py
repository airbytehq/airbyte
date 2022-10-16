#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import io

import docker
import pytest
from source_acceptance_test.utils import ConnectorRunner


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


class TestEnvAttributes:
    def test_correct_connector_image(self, correct_connector_image, tmp_path):
        docker_runner = ConnectorRunner(image_name=correct_connector_image, volume=tmp_path)
        assert docker_runner.env_variables.get("AIRBYTE_ENTRYPOINT"), "AIRBYTE_ENTRYPOINT must be set in dockerfile"
        assert docker_runner.env_variables.get("AIRBYTE_ENTRYPOINT") == " ".join(
            docker_runner.entry_point
        ), "env should be equal to space-joined entrypoint"

    def test_connector_image_without_env(self, connector_image_without_env, tmp_path):
        docker_runner = ConnectorRunner(image_name=connector_image_without_env, volume=tmp_path)
        assert not docker_runner.env_variables.get("AIRBYTE_ENTRYPOINT"), "this test should fail if AIRBYTE_ENTRYPOINT defined"

    def test_docker_image_env_ne_entrypoint(self, connector_image_with_ne_properties, tmp_path):
        docker_runner = ConnectorRunner(image_name=connector_image_with_ne_properties, volume=tmp_path)
        assert docker_runner.env_variables.get("AIRBYTE_ENTRYPOINT"), "AIRBYTE_ENTRYPOINT must be set in dockerfile"
        assert docker_runner.env_variables.get("AIRBYTE_ENTRYPOINT") != " ".join(docker_runner.entry_point), (
            "This test should fail if we have " ".join(ENTRYPOINT)==ENV"
        )
