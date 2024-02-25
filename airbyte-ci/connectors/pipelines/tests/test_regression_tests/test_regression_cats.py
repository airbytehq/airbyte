# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Type
from unittest.mock import AsyncMock

import dagger
import pytest
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.regression_test.steps.regression_cats import RegressionTestsControl, RegressionTestsTarget
from pipelines.airbyte_ci.connectors.test.steps.common import AcceptanceTests
from pipelines.helpers.connectors.modifed import ConnectorWithModifiedFiles
from pipelines.models.steps import StepStatus

pytestmark = [
    pytest.mark.anyio,
]


class TestRegressionTests:
    @staticmethod
    def get_dummy_cat_container(dagger_client: dagger.Client, test_cls: Type[AcceptanceTests], stdout: str, stderr: str):
        container = (
            dagger_client.container()
            .from_("bash:latest")
            .with_exec(["mkdir", "-p", test_cls.CONTAINER_TEST_INPUT_DIRECTORY])
            .with_exec(["mkdir", "-p", test_cls.CONTAINER_SECRETS_DIRECTORY])
        )
        return container.with_new_file("/stupid_bash_script.sh", contents=f"echo {stdout}; echo {stderr} >&2; exit 0")

    @pytest.fixture
    def test_context_ci(self, current_platform, dagger_client):
        context = ConnectorContext(
            pipeline_name="test",
            connector=ConnectorWithModifiedFiles("source-faker", frozenset()),
            git_branch="test",
            git_revision="test",
            report_output_prefix="test",
            is_local=False,
            use_remote_secrets=True,
            targeted_platforms=[current_platform],
            versions_to_test=("latest", "dev"),
        )
        context.dagger_client = dagger_client
        return context

    @pytest.fixture
    def dummy_connector_under_test_container(self, dagger_client) -> dagger.Container:
        return dagger_client.container().from_("airbyte/source-faker:latest")

    @pytest.mark.asyncio
    async def test_regression_tests_control(self, test_context_ci, mocker):
        """Test the behavior of the run function for RegressionTestsControl using a dummy container."""
        cat_container = self.get_dummy_cat_container(test_context_ci.dagger_client, RegressionTestsControl, stdout="hello", stderr="world")
        prep_container = self.get_dummy_cat_container(test_context_ci.dagger_client, RegressionTestsControl, stdout="hello", stderr="world")
        mock_prepare = AsyncMock(return_value=prep_container)
        mock_export = AsyncMock()

        mocker.patch.object(RegressionTestsControl, "_build_connector_acceptance_test", side_effect=AsyncMock(return_value=cat_container))
        mocker.patch.object(RegressionTestsControl, "get_cat_command", return_value=["bash", "/stupid_bash_script.sh"])
        RegressionTestsControl._prepare_regression_test = mock_prepare
        RegressionTestsControl._export_control_output = mock_export
        test_context_ci.get_connector_dir = mocker.AsyncMock(return_value=".")
        acceptance_test_step = RegressionTestsControl(test_context_ci)
        step_result = await acceptance_test_step._run(None)
        assert step_result.status == StepStatus.SUCCESS
        mock_prepare.assert_awaited_once()
        mock_export.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_regression_tests_target(self, test_context_ci, mocker):
        """Test the behavior of the run function for RegressionTestsTarget using a dummy container."""
        cat_container = self.get_dummy_cat_container(test_context_ci.dagger_client, RegressionTestsTarget, stdout="hello", stderr="world")
        mocker.patch.object(RegressionTestsTarget, "_build_connector_acceptance_test", side_effect=AsyncMock(return_value=cat_container))
        mocker.patch.object(RegressionTestsTarget, "get_cat_command", return_value=["bash", "/stupid_bash_script.sh"])
        test_context_ci.get_connector_dir = mocker.AsyncMock(return_value=".")
        acceptance_test_step = RegressionTestsTarget(test_context_ci)
        step_result = await acceptance_test_step._run(None)
        assert step_result.status == StepStatus.SUCCESS
