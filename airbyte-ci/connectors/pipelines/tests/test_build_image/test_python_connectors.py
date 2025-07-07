#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

import asyncclick as click
import pytest

from pipelines.airbyte_ci.connectors.build_image.steps import build_customization, python_connectors
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.consts import BUILD_PLATFORMS
from pipelines.models.steps import StepStatus
from tests.utils import mock_container

pytestmark = [
    pytest.mark.anyio,
]


class TestBuildConnectorImage:
    @pytest.fixture
    def all_platforms(self):
        return BUILD_PLATFORMS

    @pytest.fixture
    def test_context(self, mocker):
        return mocker.Mock(secrets_to_mask=[], targeted_platforms=BUILD_PLATFORMS)

    @pytest.fixture
    def test_context_with_connector_with_base_image(self, test_context):
        test_context.connector.metadata = {
            "connectorBuildOptions": {"baseImage": "xyz"},
            "dockerImageTag": "0.0.0",
            "dockerRepository": "test",
        }
        return test_context

    @pytest.fixture
    def test_context_with_connector_without_base_image(self, test_context):
        test_context.connector.metadata = {"dockerImageTag": "0.0.0", "dockerRepository": "test"}
        return test_context

    @pytest.fixture
    def connector_with_base_image_no_build_customization(self, all_connectors):
        for connector in all_connectors:
            if connector.metadata and connector.metadata.get("connectorBuildOptions", {}).get("baseImage"):
                if not (connector.code_directory / "build_customization.py").exists():
                    return connector
        pytest.skip("No connector with a connectorBuildOptions.baseImage metadata found")

    @pytest.fixture
    def connector_with_base_image_with_build_customization(self, connector_with_base_image_no_build_customization):
        dummy_build_customization = (Path(__file__).parent / "dummy_build_customization.py").read_text()
        (connector_with_base_image_no_build_customization.code_directory / "build_customization.py").write_text(dummy_build_customization)
        yield connector_with_base_image_no_build_customization
        (connector_with_base_image_no_build_customization.code_directory / "build_customization.py").unlink()

    @pytest.fixture
    def test_context_with_real_connector_using_base_image(
        self, connector_with_base_image_no_build_customization, dagger_client, current_platform
    ):
        context = ConnectorContext(
            pipeline_name="test build",
            connector=connector_with_base_image_no_build_customization,
            git_branch="test",
            git_revision="test",
            diffed_branch="test",
            git_repo_url="test",
            report_output_prefix="test",
            is_local=True,
            targeted_platforms=[current_platform],
        )
        context.dagger_client = dagger_client
        return context

    @pytest.fixture
    def test_context_with_real_connector_using_base_image_with_build_customization(
        self, connector_with_base_image_with_build_customization, dagger_client, current_platform
    ):
        context = ConnectorContext(
            pipeline_name="test build",
            connector=connector_with_base_image_with_build_customization,
            git_branch="test",
            git_revision="test",
            diffed_branch="test",
            git_repo_url="test",
            report_output_prefix="test",
            is_local=True,
            targeted_platforms=[current_platform],
        )
        context.dagger_client = dagger_client
        return context

    @pytest.fixture
    def connector_without_base_image(self, all_connectors):
        for connector in all_connectors:
            if connector.metadata and not connector.metadata.get("connectorBuildOptions", {}).get("baseImage"):
                return connector
        pytest.skip("No connector without a connectorBuildOptions.baseImage metadata found")

    @pytest.fixture
    def test_context_with_real_connector_without_base_image(self, connector_without_base_image, dagger_client, current_platform):
        context = ConnectorContext(
            pipeline_name="test build",
            connector=connector_without_base_image,
            git_branch="test",
            git_revision="test",
            diffed_branch="test",
            git_repo_url="test",
            report_output_prefix="test",
            is_local=True,
            targeted_platforms=[current_platform],
        )
        context.dagger_client = dagger_client
        return context

    async def test__run_using_base_image_with_mocks(self, mocker, test_context_with_connector_with_base_image, all_platforms):
        container_built_from_base = mock_container()

        mocker.patch.object(
            python_connectors.BuildConnectorImages, "_build_from_base_image", mocker.AsyncMock(return_value=container_built_from_base)
        )
        mocker.patch.object(python_connectors.BuildConnectorImages, "get_step_result", mocker.AsyncMock())
        step = python_connectors.BuildConnectorImages(test_context_with_connector_with_base_image)
        step_result = await step._run()
        assert step._build_from_base_image.call_count == len(all_platforms)
        container_built_from_base.with_exec.assert_called_with(["spec"], use_entrypoint=True)
        assert step_result.status is StepStatus.SUCCESS
        for platform in all_platforms:
            assert step_result.output[platform] == container_built_from_base

    @pytest.mark.slow
    async def test_building_from_base_image_for_real(self, test_context_with_real_connector_using_base_image, current_platform):
        step = python_connectors.BuildConnectorImages(test_context_with_real_connector_using_base_image)
        step_result = await step._run()
        step_result.status is StepStatus.SUCCESS
        built_container = step_result.output[current_platform]
        assert await built_container.env_variable("AIRBYTE_ENTRYPOINT") == " ".join(
            build_customization.get_entrypoint(step.context.connector)
        )
        assert await built_container.workdir() == step.PATH_TO_INTEGRATION_CODE
        assert await built_container.entrypoint() == build_customization.get_entrypoint(step.context.connector)
        assert (
            await built_container.label("io.airbyte.version")
            == test_context_with_real_connector_using_base_image.connector.metadata["dockerImageTag"]
        )
        assert (
            await built_container.label("io.airbyte.name")
            == test_context_with_real_connector_using_base_image.connector.metadata["dockerRepository"]
        )

    @pytest.mark.slow
    async def test_building_from_base_image_with_customization_for_real(
        self, test_context_with_real_connector_using_base_image_with_build_customization, current_platform
    ):
        step = python_connectors.BuildConnectorImages(test_context_with_real_connector_using_base_image_with_build_customization)
        step_result = await step._run()
        step_result.status is StepStatus.SUCCESS
        built_container = step_result.output[current_platform]
        assert await built_container.env_variable("MY_PRE_BUILD_ENV_VAR") == "my_pre_build_env_var_value"
        assert await built_container.env_variable("MY_POST_BUILD_ENV_VAR") == "my_post_build_env_var_value"

    async def test__run_using_base_dockerfile_with_mocks(self, mocker, test_context_with_connector_without_base_image, all_platforms):
        container_built_from_dockerfile = mock_container()
        mocker.patch.object(
            python_connectors.BuildConnectorImages, "_build_from_dockerfile", mocker.AsyncMock(return_value=container_built_from_dockerfile)
        )
        step = python_connectors.BuildConnectorImages(test_context_with_connector_without_base_image)
        step_result = await step._run()
        assert step._build_from_dockerfile.call_count == len(all_platforms)
        container_built_from_dockerfile.with_exec.assert_called_with(["spec"], use_entrypoint=True)
        assert step_result.status is StepStatus.SUCCESS
        for platform in all_platforms:
            assert step_result.output[platform] == container_built_from_dockerfile

    async def test_building_from_dockerfile_for_real(self, test_context_with_real_connector_without_base_image):
        step = python_connectors.BuildConnectorImages(test_context_with_real_connector_without_base_image)
        step_result = await step._run()
        step_result.status is StepStatus.SUCCESS
