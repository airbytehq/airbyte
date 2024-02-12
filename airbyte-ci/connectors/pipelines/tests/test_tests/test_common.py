#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import pathlib
import time
from typing import List

import dagger
import pytest
import yaml
from freezegun import freeze_time
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.test.steps import common
from pipelines.dagger.actions.system import docker
from pipelines.helpers.connectors.modifed import ConnectorWithModifiedFiles
from pipelines.models.steps import StepStatus

pytestmark = [
    pytest.mark.anyio,
]


class TestAcceptanceTests:
    @staticmethod
    def get_dummy_cat_container(dagger_client: dagger.Client, exit_code: int, secret_file_paths: List, stdout: str, stderr: str):
        secret_file_paths = secret_file_paths or []
        container = (
            dagger_client.container()
            .from_("bash:latest")
            .with_exec(["mkdir", "-p", common.AcceptanceTests.CONTAINER_TEST_INPUT_DIRECTORY])
            .with_exec(["mkdir", "-p", common.AcceptanceTests.CONTAINER_SECRETS_DIRECTORY])
        )

        for secret_file_path in secret_file_paths:
            secret_dir_name = str(pathlib.Path(secret_file_path).parent)
            container = container.with_exec(["mkdir", "-p", secret_dir_name])
            container = container.with_exec(["sh", "-c", f"echo foo > {secret_file_path}"])
        return container.with_new_file("/stupid_bash_script.sh", contents=f"echo {stdout}; echo {stderr} >&2; exit {exit_code}")

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
        )
        context.dagger_client = dagger_client
        return context

    @pytest.fixture
    def dummy_connector_under_test_container(self, dagger_client) -> dagger.Container:
        return dagger_client.container().from_("airbyte/source-faker:latest")

    @pytest.fixture
    def another_dummy_connector_under_test_container(self, dagger_client) -> dagger.File:
        return dagger_client.container().from_("airbyte/source-pokeapi:latest")

    async def test_skipped_when_no_acceptance_test_config(self, mocker, test_context_ci):
        test_context_ci.connector = mocker.MagicMock(acceptance_test_config=None)
        acceptance_test_step = common.AcceptanceTests(test_context_ci)
        step_result = await acceptance_test_step._run(None)
        assert step_result.status == StepStatus.SKIPPED

    @pytest.mark.parametrize(
        "exit_code,expected_status,secrets_file_names,expect_updated_secrets",
        [
            (0, StepStatus.SUCCESS, [], False),
            (1, StepStatus.FAILURE, [], False),
            (2, StepStatus.FAILURE, [], False),
            (common.AcceptanceTests.skipped_exit_code, StepStatus.SKIPPED, [], False),
            (0, StepStatus.SUCCESS, [f"{common.AcceptanceTests.CONTAINER_SECRETS_DIRECTORY}/config.json"], False),
            (1, StepStatus.FAILURE, [f"{common.AcceptanceTests.CONTAINER_SECRETS_DIRECTORY}/config.json"], False),
            (2, StepStatus.FAILURE, [f"{common.AcceptanceTests.CONTAINER_SECRETS_DIRECTORY}/config.json"], False),
            (
                common.AcceptanceTests.skipped_exit_code,
                StepStatus.SKIPPED,
                [f"{common.AcceptanceTests.CONTAINER_SECRETS_DIRECTORY}/config.json"],
                False,
            ),
            (
                0,
                StepStatus.SUCCESS,
                [
                    f"{common.AcceptanceTests.CONTAINER_SECRETS_DIRECTORY}/config.json",
                    f"{common.AcceptanceTests.CONTAINER_SECRETS_DIRECTORY}/updated_configurations/updated_config.json",
                ],
                True,
            ),
            (
                1,
                StepStatus.FAILURE,
                [
                    f"{common.AcceptanceTests.CONTAINER_SECRETS_DIRECTORY}/config.json",
                    f"{common.AcceptanceTests.CONTAINER_SECRETS_DIRECTORY}/updated_configurations/updated_config.json",
                ],
                True,
            ),
            (
                2,
                StepStatus.FAILURE,
                [
                    f"{common.AcceptanceTests.CONTAINER_SECRETS_DIRECTORY}/config.json",
                    f"{common.AcceptanceTests.CONTAINER_SECRETS_DIRECTORY}/updated_configurations/updated_config.json",
                ],
                True,
            ),
            (
                common.AcceptanceTests.skipped_exit_code,
                StepStatus.SKIPPED,
                [
                    f"{common.AcceptanceTests.CONTAINER_SECRETS_DIRECTORY}/config.json",
                    f"{common.AcceptanceTests.CONTAINER_SECRETS_DIRECTORY}/updated_configurations/updated_config.json",
                ],
                True,
            ),
        ],
    )
    async def test__run(
        self,
        test_context_ci,
        mocker,
        exit_code: int,
        expected_status: StepStatus,
        secrets_file_names: List,
        expect_updated_secrets: bool,
        test_input_dir: dagger.Directory,
    ):
        """Test the behavior of the run function using a dummy container."""
        cat_container = self.get_dummy_cat_container(
            test_context_ci.dagger_client, exit_code, secrets_file_names, stdout="hello", stderr="world"
        )
        async_mock = mocker.AsyncMock(return_value=cat_container)
        mocker.patch.object(common.AcceptanceTests, "_build_connector_acceptance_test", side_effect=async_mock)
        mocker.patch.object(common.AcceptanceTests, "get_cat_command", return_value=["bash", "/stupid_bash_script.sh"])
        test_context_ci.get_connector_dir = mocker.AsyncMock(return_value=test_input_dir)
        acceptance_test_step = common.AcceptanceTests(test_context_ci)
        step_result = await acceptance_test_step._run(None)
        assert step_result.status == expected_status
        assert step_result.stdout.strip() == "hello"
        assert step_result.stderr.strip() == "world"
        if expect_updated_secrets:
            assert (
                await test_context_ci.updated_secrets_dir.entries()
                == await cat_container.directory(f"{common.AcceptanceTests.CONTAINER_SECRETS_DIRECTORY}").entries()
            )
            assert any("updated_configurations" in str(file_name) for file_name in await test_context_ci.updated_secrets_dir.entries())

    @pytest.fixture
    def test_input_dir(self, dagger_client, tmpdir):
        with open(tmpdir / "acceptance-test-config.yml", "w") as f:
            yaml.safe_dump({"connector_image": "airbyte/connector_under_test_image:dev"}, f)
        return dagger_client.host().directory(str(tmpdir))

    def get_patched_acceptance_test_step(self, dagger_client, mocker, test_context_ci, test_input_dir):
        test_secrets = {"config.json": dagger_client.set_secret("config.json", "connector_secret")}
        test_context_ci.get_connector_dir = mocker.AsyncMock(return_value=test_input_dir)
        test_context_ci.connector_acceptance_test_image = "bash:latest"
        test_context_ci.get_connector_secrets = mocker.AsyncMock(return_value=test_secrets)

        mocker.patch.object(docker, "load_image_to_docker_host", return_value="image_sha")
        mocker.patch.object(docker, "with_bound_docker_host", lambda _, cat_container: cat_container)
        return common.AcceptanceTests(test_context_ci)

    async def test_cat_container_provisioning(
        self, dagger_client, mocker, test_context_ci, test_input_dir, dummy_connector_under_test_container
    ):
        """Check that the acceptance test container is correctly provisioned.
        We check that:
            - the test input and secrets are correctly mounted.
            - the cache buster and image sha are correctly set as environment variables.
            - that the entrypoint is correctly set.
            - the current working directory is correctly set.
        """
        # The mounted_connector_secrets behaves differently when the test is run locally or in CI.
        # It is not masking the secrets when run locally.
        # We want to confirm that the secrets are correctly masked when run in CI.

        acceptance_test_step = self.get_patched_acceptance_test_step(dagger_client, mocker, test_context_ci, test_input_dir)
        cat_container = await acceptance_test_step._build_connector_acceptance_test(dummy_connector_under_test_container, test_input_dir)
        assert (await cat_container.with_exec(["pwd"]).stdout()).strip() == acceptance_test_step.CONTAINER_TEST_INPUT_DIRECTORY
        test_input_ls_result = await cat_container.with_exec(["ls"]).stdout()
        assert all(
            file_or_directory in test_input_ls_result.splitlines() for file_or_directory in ["secrets", "acceptance-test-config.yml"]
        )
        assert await cat_container.with_exec(["cat", f"{acceptance_test_step.CONTAINER_SECRETS_DIRECTORY}/config.json"]).stdout() == "***"
        env_vars = {await env_var.name(): await env_var.value() for env_var in await cat_container.env_variables()}
        assert "CACHEBUSTER" in env_vars

    async def test_cat_container_caching(
        self,
        dagger_client,
        mocker,
        test_context_ci,
        test_input_dir,
        dummy_connector_under_test_container,
        another_dummy_connector_under_test_container,
    ):
        """Check that the acceptance test container caching behavior is correct."""

        initial_datetime = datetime.datetime(year=1992, month=6, day=19, hour=13, minute=1, second=0)

        with freeze_time(initial_datetime) as frozen_datetime:
            acceptance_test_step = self.get_patched_acceptance_test_step(dagger_client, mocker, test_context_ci, test_input_dir)
            first_cat_container = await acceptance_test_step._build_connector_acceptance_test(
                dummy_connector_under_test_container, test_input_dir
            )
            fist_date_result = await first_cat_container.with_exec(["date"]).stdout()

            frozen_datetime.tick(delta=datetime.timedelta(hours=5))
            # Check that cache is used in the same day
            second_cat_container = await acceptance_test_step._build_connector_acceptance_test(
                dummy_connector_under_test_container, test_input_dir
            )

            second_date_result = await second_cat_container.with_exec(["date"]).stdout()
            assert fist_date_result == second_date_result

            # Check that cache bursted after a day
            frozen_datetime.tick(delta=datetime.timedelta(days=1, minutes=10))
            third_cat_container = await acceptance_test_step._build_connector_acceptance_test(
                dummy_connector_under_test_container, test_input_dir
            )
            third_date_result = await third_cat_container.with_exec(["date"]).stdout()
            assert third_date_result != second_date_result

            time.sleep(1)
            # Check that changing the container invalidates the cache
            fourth_cat_container = await acceptance_test_step._build_connector_acceptance_test(
                another_dummy_connector_under_test_container, test_input_dir
            )
            fourth_date_result = await fourth_cat_container.with_exec(["date"]).stdout()
            assert fourth_date_result != third_date_result

    async def test_params(self, dagger_client, mocker, test_context_ci, test_input_dir):
        acceptance_test_step = self.get_patched_acceptance_test_step(dagger_client, mocker, test_context_ci, test_input_dir)
        assert set(acceptance_test_step.params_as_cli_options) == {"-ra", "--disable-warnings", "--durations=3"}
        acceptance_test_step.extra_params = {"--durations": ["5"], "--collect-only": []}
        assert set(acceptance_test_step.params_as_cli_options) == {"-ra", "--disable-warnings", "--durations=5", "--collect-only"}


class TestCheckBaseImageIsUsed:
    @pytest.fixture
    def certified_connector_no_base_image(self, all_connectors):
        for connector in all_connectors:
            if connector.metadata.get("supportLevel") == "certified":
                if connector.metadata.get("connectorBuildOptions", {}).get("baseImage") is None:
                    return connector
        pytest.skip("No certified connector without base image found")

    @pytest.fixture
    def certified_connector_with_base_image(self, all_connectors):
        for connector in all_connectors:
            if connector.metadata.get("supportLevel") == "certified":
                if connector.metadata.get("connectorBuildOptions", {}).get("baseImage") is not None:
                    return connector
        pytest.skip("No certified connector with base image found")

    @pytest.fixture
    def community_connector_no_base_image(self, all_connectors):
        for connector in all_connectors:
            if connector.metadata.get("supportLevel") == "community":
                if connector.metadata.get("connectorBuildOptions", {}).get("baseImage") is None:
                    return connector
        pytest.skip("No certified connector without base image found")

    @pytest.fixture
    def test_context(self, mocker, dagger_client):
        return mocker.MagicMock(dagger_client=dagger_client)

    async def test_pass_on_community_connector_no_base_image(self, mocker, dagger_client, community_connector_no_base_image):
        test_context = mocker.MagicMock(dagger_client=dagger_client, connector=community_connector_no_base_image)
        check_base_image_is_used_step = common.CheckBaseImageIsUsed(test_context)
        step_result = await check_base_image_is_used_step.run()
        assert step_result.status == StepStatus.SKIPPED

    async def test_pass_on_certified_connector_with_base_image(self, mocker, dagger_client, certified_connector_with_base_image):
        dagger_connector_dir = dagger_client.host().directory(str(certified_connector_with_base_image.code_directory))
        test_context = mocker.MagicMock(
            dagger_client=dagger_client,
            connector=certified_connector_with_base_image,
            get_connector_dir=mocker.AsyncMock(return_value=dagger_connector_dir),
        )
        check_base_image_is_used_step = common.CheckBaseImageIsUsed(test_context)
        step_result = await check_base_image_is_used_step.run()
        assert step_result.status == StepStatus.SUCCESS

    async def test_fail_on_certified_connector_no_base_image(self, mocker, dagger_client, certified_connector_no_base_image):
        test_context = mocker.MagicMock(dagger_client=dagger_client, connector=certified_connector_no_base_image)
        check_base_image_is_used_step = common.CheckBaseImageIsUsed(test_context)
        step_result = await check_base_image_is_used_step.run()
        assert step_result.status == StepStatus.FAILURE


class TestCheckPythonRegistryPublishConfiguration:
    @pytest.fixture
    def test_context(self, mocker, dagger_client):
        return mocker.MagicMock(dagger_client=dagger_client)

    def _get_connector_with_metadata(self, mocker, tags, support_level, pypi=None):
        connector = mocker.MagicMock()
        connector.metadata = {
            "supportLevel": support_level,
            "tags": tags,
            "connectorType": "source",
        }
        if pypi:
            connector.metadata["remoteRegistries"] = {"pypi": pypi}
        return connector

    async def test_pass_on_community_connector_not_published(self, mocker, dagger_client):
        test_context = mocker.MagicMock(
            dagger_client=dagger_client, connector=self._get_connector_with_metadata(mocker, ["language:python"], "community")
        )
        check_python_registry_config = common.CheckPythonRegistryPublishConfiguration(test_context)
        step_result = await check_python_registry_config.run()
        assert step_result.status == StepStatus.SKIPPED

    async def test_pass_on_java_connector_not_published(self, mocker, dagger_client):
        test_context = mocker.MagicMock(
            dagger_client=dagger_client, connector=self._get_connector_with_metadata(mocker, ["language:java"], "certified")
        )
        check_python_registry_config = common.CheckPythonRegistryPublishConfiguration(test_context)
        step_result = await check_python_registry_config.run()
        assert step_result.status == StepStatus.SKIPPED

    async def test_pass_on_certified_connector_published(self, mocker, dagger_client):
        test_context = mocker.MagicMock(
            dagger_client=dagger_client,
            connector=self._get_connector_with_metadata(mocker, ["language:python"], "certified", {"enabled": True}),
        )
        check_python_registry_config = common.CheckPythonRegistryPublishConfiguration(test_context)
        step_result = await check_python_registry_config.run()
        assert step_result.status == StepStatus.SUCCESS

    async def test_pass_on_community_connector_published(self, mocker, dagger_client):
        test_context = mocker.MagicMock(
            dagger_client=dagger_client,
            connector=self._get_connector_with_metadata(mocker, ["language:python"], "community", {"enabled": True}),
        )
        check_python_registry_config = common.CheckPythonRegistryPublishConfiguration(test_context)
        step_result = await check_python_registry_config.run()
        assert step_result.status == StepStatus.SUCCESS

    async def test_fail_on_certified_connector_not_published(self, mocker, dagger_client):
        test_context = mocker.MagicMock(
            dagger_client=dagger_client,
            connector=self._get_connector_with_metadata(mocker, ["language:python"], "certified", {"enabled": False}),
        )
        check_python_registry_config = common.CheckPythonRegistryPublishConfiguration(test_context)
        step_result = await check_python_registry_config.run()
        assert step_result.status == StepStatus.FAILURE
