#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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
    image, iterools_tee = client.images.build(fileobj=fileobj, tag=tag, forcerm=True, rm=True)
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
