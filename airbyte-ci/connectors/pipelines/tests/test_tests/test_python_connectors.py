#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import patch

import asyncclick as click
import pytest
from connector_ops.utils import Connector, ConnectorLanguage

from pipelines.airbyte_ci.connectors.build_image.steps.python_connectors import BuildConnectorImages
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.test.steps.python_connectors import PyAirbyteValidation, UnitTests
from pipelines.models.steps import StepResult, StepStatus

pytestmark = [
    pytest.mark.anyio,
]


class TestUnitTests:
    @pytest.fixture
    def connector_with_poetry(self):
        return Connector("destination-duckdb")

    @pytest.fixture
    def certified_connector_with_setup(self, all_connectors):
        for connector in all_connectors:
            if connector.support_level == "certified" and connector.language in [ConnectorLanguage.LOW_CODE, ConnectorLanguage.PYTHON]:
                if connector.code_directory.joinpath("setup.py").exists():
                    return connector
        pytest.skip("No certified connector with setup.py found.")

    @pytest.fixture
    def context_for_certified_connector_with_setup(self, mocker, certified_connector_with_setup, dagger_client, current_platform):
        context = ConnectorContext(
            pipeline_name="test unit tests",
            connector=certified_connector_with_setup,
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
    async def certified_container_with_setup(self, context_for_certified_connector_with_setup, current_platform):
        result = await BuildConnectorImages(context_for_certified_connector_with_setup).run()
        return result.output[current_platform]

    @pytest.fixture
    def context_for_connector_with_poetry(self, mocker, connector_with_poetry, dagger_client, current_platform):
        context = ConnectorContext(
            pipeline_name="test unit tests",
            connector=connector_with_poetry,
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
    async def container_with_poetry(self, context_for_connector_with_poetry, current_platform):
        result = await BuildConnectorImages(context_for_connector_with_poetry).run()
        return result.output[current_platform]

    async def test__run_for_setup_py(self, context_for_certified_connector_with_setup, certified_container_with_setup):
        # Assume that the tests directory is available
        result = await UnitTests(context_for_certified_connector_with_setup)._run(certified_container_with_setup)
        assert isinstance(result, StepResult)
        assert "test session starts" in result.stdout or "test session starts" in result.stderr
        assert (
            "Total coverage:" in result.stdout
        ), "The pytest-cov package should be installed in the test environment and test coverage report should be displayed."
        assert "Required test coverage of" in result.stdout, "A test coverage threshold should be defined for certified connectors."
        pip_freeze_output = await result.output.with_exec(["pip", "freeze"]).stdout()
        assert (
            context_for_certified_connector_with_setup.connector.technical_name in pip_freeze_output
        ), "The connector should be installed in the test environment."
        assert "pytest" in pip_freeze_output, "The pytest package should be installed in the test environment."
        assert "pytest-cov" in pip_freeze_output, "The pytest-cov package should be installed in the test environment."

    async def test__run_for_poetry(self, context_for_connector_with_poetry, container_with_poetry):
        # Assume that the tests directory is available
        result = await UnitTests(context_for_connector_with_poetry).run(container_with_poetry)
        assert isinstance(result, StepResult)
        # We only check for the presence of "test session starts" because we have no guarantee that the tests will pass
        assert "test session starts" in result.stdout or "test session starts" in result.stderr, "The pytest tests should have started."
        pip_freeze_output = await result.output.with_exec(["poetry", "run", "pip", "freeze"]).stdout()

        assert (
            context_for_connector_with_poetry.connector.technical_name in pip_freeze_output
        ), "The connector should be installed in the test environment."
        assert "pytest" in pip_freeze_output, "The pytest package should be installed in the test environment."

    def test_params(self, context_for_certified_connector_with_setup):
        step = UnitTests(context_for_certified_connector_with_setup)
        assert step.params_as_cli_options == [
            "-s",
            f"--cov={context_for_certified_connector_with_setup.connector.technical_name.replace('-', '_')}",
            f"--cov-fail-under={step.MINIMUM_COVERAGE_FOR_CERTIFIED_CONNECTORS}",
        ]


class TestPyAirbyteValidationTests:
    @pytest.fixture
    def compatible_connector(self):
        return Connector("source-faker")

    @pytest.fixture
    def incompatible_connector(self):
        return Connector("source-postgres")

    @pytest.fixture
    def context_for_valid_connector(self, compatible_connector, dagger_client, current_platform):
        context = ConnectorContext(
            pipeline_name="CLI smoke test with PyAirbyte",
            connector=compatible_connector,
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
    def context_for_invalid_connector(self, incompatible_connector, dagger_client, current_platform):
        context = ConnectorContext(
            pipeline_name="CLI smoke test with PyAirbyte",
            connector=incompatible_connector,
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

    async def test__run_validation_success(self, mocker, context_for_valid_connector: ConnectorContext):
        result = await PyAirbyteValidation(context_for_valid_connector)._run(mocker.MagicMock())
        assert isinstance(result, StepResult)
        assert result.status == StepStatus.SUCCESS
        assert "Getting `spec` output from connector..." in result.stdout

    async def test__run_validation_skip_unpublished_connector(
        self,
        mocker,
        context_for_invalid_connector: ConnectorContext,
    ):
        result = await PyAirbyteValidation(context_for_invalid_connector)._run(mocker.MagicMock())
        assert isinstance(result, StepResult)
        assert result.status == StepStatus.SKIPPED

    async def test__run_validation_fail(
        self,
        mocker,
        context_for_invalid_connector: ConnectorContext,
    ):
        metadata = context_for_invalid_connector.connector.metadata
        metadata["remoteRegistries"] = {"pypi": {"enabled": True, "packageName": "airbyte-source-postgres"}}
        metadata_mock = mocker.PropertyMock(return_value=metadata)
        with patch.object(Connector, "metadata", metadata_mock):
            result = await PyAirbyteValidation(context_for_invalid_connector)._run(mocker.MagicMock())
            assert isinstance(result, StepResult)
            assert result.status == StepStatus.FAILURE
            assert "is not installable" in result.stderr
