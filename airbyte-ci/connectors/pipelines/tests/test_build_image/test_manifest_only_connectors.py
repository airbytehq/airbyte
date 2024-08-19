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

    async def test__run_using_base_image_with_mocks(self, mocker, test_context_with_connector_with_base_image, all_platforms):
        container_built_from_base = mock_container()
        container_built_from_base.with_label.return_value = container_built_from_base

        mocker.patch.object(
            manifest_only_connectors.BuildConnectorImages,
            "_build_from_base_image",
            mocker.AsyncMock(return_value=container_built_from_base),
        )
        mocker.patch.object(manifest_only_connectors.BuildConnectorImages, "get_step_result", mocker.AsyncMock())
        step = manifest_only_connectors.BuildConnectorImages(test_context_with_connector_with_base_image)
        step_result = await step._run()
        assert step._build_from_base_image.call_count == len(all_platforms)
        container_built_from_base.with_exec.assert_called_with(["spec"])
        container_built_from_base.with_label.assert_any_call(
            "io.airbyte.version", test_context_with_connector_with_base_image.connector.metadata["dockerImageTag"]
        )
        container_built_from_base.with_label.assert_any_call(
            "io.airbyte.name", test_context_with_connector_with_base_image.connector.metadata["dockerRepository"]
        )

        assert step_result.status is StepStatus.SUCCESS
        for platform in all_platforms:
            assert step_result.output[platform] == container_built_from_base
