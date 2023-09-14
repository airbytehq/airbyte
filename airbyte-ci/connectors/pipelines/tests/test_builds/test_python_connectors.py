#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from pipelines.bases import StepStatus
from pipelines.builds.python_connectors import BuildConnectorImage
from pipelines.contexts import ConnectorContext

pytestmark = [
    pytest.mark.anyio,
]


class TestBuildConnectorImage:
    @pytest.fixture
    def test_context(self, mocker):
        return mocker.Mock(secrets_to_mask=[])

    @pytest.fixture
    def test_context_with_connector_with_base_image(self, test_context):
        test_context.connector.metadata = {"connectorBuildOptions": {"baseImage": "xyz"}}
        return test_context

    @pytest.fixture
    def test_context_with_connector_without_base_image(self, test_context):
        test_context.connector.metadata = {}
        return test_context

    @pytest.fixture
    def connector_with_base_image(self, all_connectors):
        for connector in all_connectors:
            if connector.metadata and connector.metadata.get("connectorBuildOptions", {}).get("baseImage"):
                return connector
        pytest.skip("No connector with a connectorBuildOptions.baseImage metadata found")

    @pytest.fixture
    def test_context_with_real_connector_using_base_image(self, connector_with_base_image, dagger_client):
        context = ConnectorContext(
            pipeline_name="test build",
            connector=connector_with_base_image,
            git_branch="test",
            git_revision="test",
            report_output_prefix="test",
            is_local=True,
            use_remote_secrets=True,
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
    def test_context_with_real_connector_without_base_image(self, connector_without_base_image, dagger_client):
        context = ConnectorContext(
            pipeline_name="test build",
            connector=connector_without_base_image,
            git_branch="test",
            git_revision="test",
            report_output_prefix="test",
            is_local=True,
            use_remote_secrets=True,
        )
        context.dagger_client = dagger_client
        return context

    async def test__run_using_base_image_with_mocks(self, mocker, test_context_with_connector_with_base_image, current_platform):
        container_built_from_base = mocker.Mock()
        mocker.patch.object(BuildConnectorImage, "_build_from_base_image", mocker.AsyncMock(return_value=container_built_from_base))
        mocker.patch.object(BuildConnectorImage, "get_step_result", mocker.AsyncMock())
        step = BuildConnectorImage(test_context_with_connector_with_base_image, current_platform)
        step_result = await step._run()
        step._build_from_base_image.assert_called_once()
        step.get_step_result.assert_called_once_with(container_built_from_base.with_exec.return_value)
        container_built_from_base.with_exec.assert_called_once_with(["spec"])
        assert step_result == step.get_step_result.return_value

    async def test_building_from_base_image_for_real(self, test_context_with_real_connector_using_base_image, current_platform):
        step = BuildConnectorImage(test_context_with_real_connector_using_base_image, current_platform)
        step_result = await step._run()
        step_result.status is StepStatus.SUCCESS
        built_container = step_result.output_artifact
        assert await built_container.env_variable("AIRBYTE_ENTRYPOINT") == " ".join(step.DEFAULT_ENTRYPOINT)
        assert await built_container.workdir() == step.PATH_TO_INTEGRATION_CODE
        assert await built_container.entrypoint() == step.DEFAULT_ENTRYPOINT
        assert (
            await built_container.label("io.airbyte.version")
            == test_context_with_real_connector_using_base_image.connector.metadata["dockerImageTag"]
        )
        assert (
            await built_container.label("io.airbyte.name")
            == test_context_with_real_connector_using_base_image.connector.metadata["dockerRepository"]
        )

    async def test__run_using_base_dockerfile_with_mocks(self, mocker, test_context_with_connector_without_base_image, current_platform):
        container_built_from_dockerfile = mocker.Mock()
        mocker.patch.object(BuildConnectorImage, "_build_from_dockerfile", mocker.AsyncMock(return_value=container_built_from_dockerfile))
        mocker.patch.object(BuildConnectorImage, "get_step_result", mocker.AsyncMock())
        step = BuildConnectorImage(test_context_with_connector_without_base_image, current_platform)
        step_result = await step._run()
        step._build_from_dockerfile.assert_called_once()
        step.get_step_result.assert_called_once_with(container_built_from_dockerfile.with_exec.return_value)
        container_built_from_dockerfile.with_exec.assert_called_once_with(["spec"])
        assert step_result == step.get_step_result.return_value

    async def test_building_from_dockerfile_for_real(self, test_context_with_real_connector_without_base_image, current_platform):
        step = BuildConnectorImage(test_context_with_real_connector_without_base_image, current_platform)
        step_result = await step._run()
        step_result.status is StepStatus.SUCCESS
