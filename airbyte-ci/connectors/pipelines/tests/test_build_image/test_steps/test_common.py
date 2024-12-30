#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os

import dagger
import docker
import pytest

from pipelines.airbyte_ci.connectors.build_image.steps import common
from pipelines.consts import LOCAL_BUILD_PLATFORM
from pipelines.models.steps import StepStatus

pytestmark = [
    pytest.mark.anyio,
]


@pytest.mark.slow
class TestLoadContainerToLocalDockerHost:
    @pytest.fixture(scope="class")
    def faker_connector(self, all_connectors):
        for connector in all_connectors:
            if connector.technical_name == "source-faker":
                return connector
        pytest.fail("Could not find the source-faker connector.")

    @pytest.fixture
    def test_context(self, mocker, dagger_client, faker_connector, tmp_path):
        return mocker.Mock(
            secrets_to_mask=[],
            dagger_client=dagger_client,
            connector=faker_connector,
            host_image_export_dir_path=tmp_path,
            git_revision="test-revision",
            diffed_branch="test-branch",
            git_repo_url="test-repo-url",
        )

    @pytest.fixture
    def bad_docker_host(self):
        original_docker_host = os.environ.get("DOCKER_HOST")
        yield "tcp://localhost:9999"
        if original_docker_host:
            os.environ["DOCKER_HOST"] = original_docker_host
        else:
            del os.environ["DOCKER_HOST"]

    @pytest.mark.parametrize(
        "platforms",
        [
            [dagger.Platform("linux/arm64")],
            [dagger.Platform("linux/amd64")],
            [dagger.Platform("linux/amd64"), dagger.Platform("linux/arm64")],
        ],
    )
    async def test_run(self, dagger_client, test_context, platforms):
        """Test that the step runs successfully and that the image is loaded in the local docker host."""
        built_containers = {
            platform: dagger_client.container(platform=platform).from_(f'{test_context.connector.metadata["dockerRepository"]}:latest')
            for platform in platforms
        }
        step = common.LoadContainerToLocalDockerHost(test_context, built_containers)

        assert step.image_tag == "dev"
        docker_client = docker.from_env()
        step.image_tag = "test-load-container"
        for platform in platforms:
            full_image_name = f"{test_context.connector.metadata['dockerRepository']}:{step.image_tag}-{platform.replace('/', '-')}"
            try:
                docker_client.images.remove(full_image_name, force=True)
            except docker.errors.ImageNotFound:
                pass
        result = await step.run()
        assert result.status is StepStatus.SUCCESS
        multi_platforms = len(platforms) > 1
        for platform in platforms:
            if multi_platforms:
                full_image_name = f"{test_context.connector.metadata['dockerRepository']}:{step.image_tag}-{platform.replace('/', '-')}"
            else:
                full_image_name = f"{test_context.connector.metadata['dockerRepository']}:{step.image_tag}"
            docker_client.images.get(full_image_name)

            # CI can't run docker arm64 containers
            if platform is LOCAL_BUILD_PLATFORM or (os.environ.get("CI", "false").lower() != "true"):
                docker_client.containers.run(full_image_name, "spec")
            docker_client.images.remove(full_image_name, force=True)

    async def test_run_export_failure(self, dagger_client, test_context, mocker):
        """Test that the step fails if the export of the container fails."""
        built_containers = {
            LOCAL_BUILD_PLATFORM: dagger_client.container(platform=LOCAL_BUILD_PLATFORM).from_(
                f'{test_context.connector.metadata["dockerRepository"]}:latest'
            )
        }
        step = common.LoadContainerToLocalDockerHost(test_context, built_containers)

        mocker.patch.object(common, "export_container_to_tarball", return_value=(None, None))
        result = await step.run()
        assert result.status is StepStatus.FAILURE
        assert "Failed to export the connector image" in result.stderr

    async def test_run_connection_error(self, dagger_client, test_context, bad_docker_host):
        """Test that the step fails if the connection to the docker host fails."""
        built_containers = {
            LOCAL_BUILD_PLATFORM: dagger_client.container(platform=LOCAL_BUILD_PLATFORM).from_(
                f'{test_context.connector.metadata["dockerRepository"]}:latest'
            )
        }
        step = common.LoadContainerToLocalDockerHost(test_context, built_containers)
        os.environ["DOCKER_HOST"] = bad_docker_host
        result = await step.run()
        assert result.status is StepStatus.FAILURE
        assert "Something went wrong while interacting with the local docker client" in result.stderr

    async def test_run_import_failure(self, dagger_client, test_context, mocker):
        """Test that the step fails if the docker import of the tar fails."""
        built_containers = {
            LOCAL_BUILD_PLATFORM: dagger_client.container(platform=LOCAL_BUILD_PLATFORM).from_(
                f'{test_context.connector.metadata["dockerRepository"]}:latest'
            )
        }
        step = common.LoadContainerToLocalDockerHost(test_context, built_containers)
        mock_docker_client = mocker.MagicMock()
        mock_docker_client.api.import_image_from_file.return_value = "bad response"
        mock_docker_client.images.load.side_effect = docker.errors.DockerException("test error")
        mocker.patch.object(common.docker, "from_env", return_value=mock_docker_client)
        result = await step.run()
        assert result.status is StepStatus.FAILURE
        assert "Something went wrong while interacting with the local docker client: test error" in result.stderr
