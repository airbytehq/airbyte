#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import pathlib
import time
from typing import List
from unittest.mock import MagicMock

import dagger
import pytest
import yaml
from pipelines.bases import StepStatus
from pipelines.tests import common

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
        return container.with_new_file("/stupid_bash_script.sh", f"echo {stdout}; echo {stderr} >&2; exit {exit_code}")

    @pytest.fixture
    def test_context(self, dagger_client):
        return MagicMock(connector=MagicMock(), dagger_client=dagger_client)

    async def test_skipped_when_no_acceptance_test_config(self, test_context):
        test_context.connector.acceptance_test_config = None
        acceptance_test_step = common.AcceptanceTests(test_context)
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
        self, test_context, mocker, exit_code: int, expected_status: StepStatus, secrets_file_names: List, expect_updated_secrets: bool
    ):
        """Test the behavior of the run function using a dummy container."""
        cat_container = self.get_dummy_cat_container(
            test_context.dagger_client, exit_code, secrets_file_names, stdout="hello", stderr="world"
        )
        async_mock = mocker.AsyncMock(return_value=cat_container)
        mocker.patch.object(common.AcceptanceTests, "_build_connector_acceptance_test", side_effect=async_mock)
        mocker.patch.object(common.AcceptanceTests, "cat_command", ["bash", "/stupid_bash_script.sh"])
        acceptance_test_step = common.AcceptanceTests(test_context)
        step_result = await acceptance_test_step._run(None)
        assert step_result.status == expected_status
        assert step_result.stdout.strip() == "hello"
        assert step_result.stderr.strip() == "world"
        if expect_updated_secrets:
            assert (
                await test_context.updated_secrets_dir.entries()
                == await cat_container.directory(f"{common.AcceptanceTests.CONTAINER_SECRETS_DIRECTORY}").entries()
            )
            assert any("updated_configurations" in str(file_name) for file_name in await test_context.updated_secrets_dir.entries())

    @pytest.fixture
    def test_input_dir(self, dagger_client, tmpdir):
        with open(tmpdir / "acceptance-test-config.yml", "w") as f:
            yaml.safe_dump({"connector_image": "airbyte/connector_under_test_image:dev"}, f)
        return dagger_client.host().directory(str(tmpdir))

    def get_patched_acceptance_test_step(self, dagger_client, mocker, test_context, test_input_dir):
        test_context.get_connector_dir = mocker.AsyncMock(return_value=test_input_dir)
        test_context.connector_acceptance_test_image = "bash:latest"
        test_context.connector_secrets = {"config.json": dagger_client.set_secret("config.json", "connector_secret")}

        mocker.patch.object(common.environments, "load_image_to_docker_host", return_value="image_sha")
        mocker.patch.object(common.environments, "with_bound_docker_host", lambda _, cat_container: cat_container)
        mocker.patch.object(common.AcceptanceTests, "get_cache_buster", return_value="cache_buster")
        return common.AcceptanceTests(test_context)

    async def test_cat_container_provisioning(self, dagger_client, mocker, test_context, test_input_dir):
        """Check that the acceptance test container is correctly provisioned.
        We check that:
            - the test input and secrets are correctly mounted.
            - the cache buster and image sha are correctly set as environment variables.
            - that the entrypoint is correctly set.
            - the current working directory is correctly set.
        """
        acceptance_test_step = self.get_patched_acceptance_test_step(dagger_client, mocker, test_context, test_input_dir)
        cat_container = await acceptance_test_step._build_connector_acceptance_test("connector_under_test_image_tar")
        assert await cat_container.entrypoint() == []
        assert (await cat_container.with_exec(["pwd"]).stdout()).strip() == acceptance_test_step.CONTAINER_TEST_INPUT_DIRECTORY
        test_input_ls_result = await cat_container.with_exec(["ls"]).stdout()
        assert all(
            file_or_directory in test_input_ls_result.splitlines() for file_or_directory in ["secrets", "acceptance-test-config.yml"]
        )
        assert await cat_container.with_exec(["cat", f"{acceptance_test_step.CONTAINER_SECRETS_DIRECTORY}/config.json"]).stdout() == "***"
        env_vars = {await env_var.name(): await env_var.value() for env_var in await cat_container.env_variables()}
        assert env_vars["CACHEBUSTER"] == "cache_buster"
        assert env_vars["CONNECTOR_IMAGE_ID"] == "image_sha"

    async def test_cat_container_caching(self, dagger_client, mocker, test_context, test_input_dir):
        """Check that the acceptance test container caching behavior is correct."""

        acceptance_test_step = self.get_patched_acceptance_test_step(dagger_client, mocker, test_context, test_input_dir)
        cat_container = await acceptance_test_step._build_connector_acceptance_test("connector_under_test_image_tar")
        cat_container = cat_container.with_exec(["date"])
        fist_date_result = await cat_container.stdout()

        time.sleep(1)
        # Check that cache is used
        cat_container = await acceptance_test_step._build_connector_acceptance_test("connector_under_test_image_tar")
        cat_container = cat_container.with_exec(["date"])
        second_date_result = await cat_container.stdout()
        assert fist_date_result == second_date_result

        time.sleep(1)
        # Check that cache buster is used to invalidate the cache
        previous_cache_buster_value = acceptance_test_step.get_cache_buster()
        new_cache_buster_value = previous_cache_buster_value + "1"
        mocker.patch.object(common.AcceptanceTests, "get_cache_buster", return_value=new_cache_buster_value)
        cat_container = await acceptance_test_step._build_connector_acceptance_test("connector_under_test_image_tar")
        cat_container = cat_container.with_exec(["date"])
        third_date_result = await cat_container.stdout()
        assert third_date_result != second_date_result

        time.sleep(1)
        # Check that image sha is used to invalidate the cache
        previous_image_sha_value = await common.environments.load_image_to_docker_host("foo", "bar", "baz")
        mocker.patch.object(common.environments, "load_image_to_docker_host", return_value=previous_image_sha_value + "1")
        cat_container = await acceptance_test_step._build_connector_acceptance_test("connector_under_test_image_tar")
        cat_container = cat_container.with_exec(["date"])
        fourth_date_result = await cat_container.stdout()
        assert fourth_date_result != third_date_result

        time.sleep(1)
        # Check the cache is used again
        cat_container = await acceptance_test_step._build_connector_acceptance_test("connector_under_test_image_tar")
        cat_container = cat_container.with_exec(["date"])
        fifth_date_result = await cat_container.stdout()
        assert fifth_date_result == fourth_date_result
