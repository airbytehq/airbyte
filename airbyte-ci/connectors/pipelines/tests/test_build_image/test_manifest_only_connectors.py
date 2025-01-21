#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

import pytest
from dagger import Container
from pipelines.airbyte_ci.connectors.build_image.steps import build_customization, common, manifest_only_connectors
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
    def mock_connector_directory(self, mocker):
        mock_components_file = mocker.Mock()
        mock_connector_dir = mocker.Mock()
        mock_connector_dir.file.return_value = mock_components_file
        return mock_connector_dir, mock_components_file

    def _assert_file_not_handled(self, container_mock, file_path):
        """Assert that a specified file_path was not handled by the container_mock"""
        assert not any(file_path in call.args[0] for call in container_mock.with_file.call_args_list)

    async def test__run_using_base_image_with_mocks(self, mocker, test_context_with_connector_with_base_image, all_platforms):
        container_built_from_base = mock_container()
        container_built_from_base.with_label.return_value = container_built_from_base

        mocker.patch.object(Path, "exists", return_value=True)  # Mock Path.exists() to always return True
        mocker.patch.object(
            manifest_only_connectors.BuildConnectorImages,
            "_build_from_base_image",
            mocker.AsyncMock(return_value=container_built_from_base),
        )
        mocker.patch.object(manifest_only_connectors.BuildConnectorImages, "get_step_result", mocker.AsyncMock())
        step = manifest_only_connectors.BuildConnectorImages(test_context_with_connector_with_base_image)
        step_result = await step._run()
        assert step._build_from_base_image.call_count == len(all_platforms)
        container_built_from_base.with_exec.assert_called_with(["spec"], use_entrypoint=True)
        container_built_from_base.with_label.assert_any_call(
            "io.airbyte.version", test_context_with_connector_with_base_image.connector.metadata["dockerImageTag"]
        )
        container_built_from_base.with_label.assert_any_call(
            "io.airbyte.name", test_context_with_connector_with_base_image.connector.metadata["dockerRepository"]
        )

        assert step_result.status is StepStatus.SUCCESS
        for platform in all_platforms:
            assert step_result.output[platform] == container_built_from_base

    @pytest.mark.parametrize("components_file_exists", [True, False])
    async def test__run_using_base_image_with_components_file(
        self, mocker, all_platforms, test_context_with_connector_with_base_image, mock_connector_directory, components_file_exists
    ):
        mock_connector_dir, mock_components_file = mock_connector_directory
        container_built_from_base = mock_container()

        container_built_from_base.with_label.return_value = container_built_from_base
        container_built_from_base.with_file.return_value = container_built_from_base

        test_context_with_connector_with_base_image.get_connector_dir = mocker.AsyncMock(return_value=mock_connector_dir)
        test_context_with_connector_with_base_image.connector.manifest_only_components_path.exists = mocker.Mock(
            return_value=components_file_exists
        )

        mocker.patch.object(
            manifest_only_connectors.BuildConnectorImages,
            "_get_base_container",
            return_value=container_built_from_base,
        )

        mocker.patch.object(
            build_customization,
            "apply_airbyte_entrypoint",
            return_value=container_built_from_base,
        )

        step = manifest_only_connectors.BuildConnectorImages(test_context_with_connector_with_base_image)

        await step._build_connector(all_platforms[0], container_built_from_base)
        if components_file_exists:
            container_built_from_base.with_file.assert_any_call("source_declarative_manifest/components.py", mock_components_file)
            mock_connector_dir.file.assert_any_call("components.py")
        else:
            self._assert_file_not_handled(container_built_from_base, "source_declarative_manifest/components.py")
