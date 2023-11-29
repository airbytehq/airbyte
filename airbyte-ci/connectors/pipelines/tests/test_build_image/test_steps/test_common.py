#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
from typing import Dict

import dagger
import docker
import pytest
from pipelines.airbyte_ci.connectors.build_image.steps import common
from pipelines.consts import BUILD_PLATFORMS
from pipelines.models.steps import StepStatus

pytestmark = [
    pytest.mark.anyio,
]


@pytest.mark.slow
class TestLoadContainerToLocalDockerHost:
    @pytest.fixture(scope="class")
    def certified_connector(self, all_connectors):
        for connector in all_connectors:
            if connector.support_level == "certified":
                return connector
        pytest.skip("No certified connector found")

    @pytest.fixture
    def built_containers(self, dagger_client, certified_connector) -> Dict[dagger.Platform, dagger.Container]:
        return {
            platform: dagger_client.container(platform=platform).from_(f'{certified_connector.metadata["dockerRepository"]}:latest')
            for platform in BUILD_PLATFORMS
        }

    @pytest.fixture
    def test_context(self, mocker, dagger_client, certified_connector, tmp_path):
        return mocker.Mock(
            secrets_to_mask=[], dagger_client=dagger_client, connector=certified_connector, host_image_export_dir_path=tmp_path
        )

    @pytest.fixture
    def step(self, test_context, built_containers):
        return common.LoadContainerToLocalDockerHost(test_context, built_containers)

    @pytest.fixture
    def bad_docker_host(self):
        original_docker_host = os.environ.get("DOCKER_HOST")
        yield "tcp://localhost:9999"
        if original_docker_host:
            os.environ["DOCKER_HOST"] = original_docker_host
        else:
            del os.environ["DOCKER_HOST"]

    async def test_run(self, test_context, step):
        """Test that the step runs successfully and that the image is loaded in the local docker host."""
        docker_client = docker.from_env()
        step.IMAGE_TAG = "test-load-container"
        try:
            docker_client.images.remove(f"{test_context.connector.metadata['dockerRepository']}:{step.IMAGE_TAG}")
        except docker.errors.ImageNotFound:
            pass
        result = await step.run()
        assert result.status is StepStatus.SUCCESS
        docker_client.images.get(f"{test_context.connector.metadata['dockerRepository']}:{step.IMAGE_TAG}")
        docker_client.images.remove(f"{test_context.connector.metadata['dockerRepository']}:{step.IMAGE_TAG}")

    async def test_run_export_failure(self, step, mocker):
        """Test that the step fails if the export of the container fails."""
        mocker.patch.object(common, "export_containers_to_tarball", return_value=(None, None))
        result = await step.run()
        assert result.status is StepStatus.FAILURE
        assert "Failed to export the connector image" in result.stderr

    async def test_run_connection_error(self, step, bad_docker_host):
        """Test that the step fails if the connection to the docker host fails."""
        os.environ["DOCKER_HOST"] = bad_docker_host
        result = await step.run()
        assert result.status is StepStatus.FAILURE
        assert "Something went wrong while interacting with the local docker client" in result.stderr

    async def test_run_import_failure(self, step, mocker):
        """Test that the step fails if the docker import of the tar fails."""
        mock_docker_client = mocker.MagicMock()
        mock_docker_client.api.import_image_from_file.return_value = "bad response"
        mocker.patch.object(common.docker, "from_env", return_value=mock_docker_client)
        result = await step.run()
        assert result.status is StepStatus.FAILURE
        assert "Failed to import the connector image" in result.stderr
