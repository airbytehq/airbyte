#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups steps made to run tests for a specific Java connector given a test context."""

from abc import ABC
from typing import ClassVar, List

from ci_connector_ops.pipelines.actions import environments, secrets
from ci_connector_ops.pipelines.bases import Step, StepResult
from ci_connector_ops.pipelines.contexts import ConnectorTestContext
from dagger import Directory


class GradleTask(Step, ABC):
    task_name: ClassVar
    BUILD_INCLUDE = [
        "airbyte-api",
        "airbyte-commons-cli",
        "airbyte-commons-protocol",
        "airbyte-commons",
        "airbyte-config",
        "airbyte-connector-test-harnesses",
        "airbyte-db",
        "airbyte-integrations/bases",
        "airbyte-integrations/connectors/source-jdbc",
        "airbyte-integrations/connectors/source-relational-db",
        "airbyte-json-validation",
        "airbyte-protocol",
        "airbyte-test-utils",
        "buildSrc",
        "tools/bin/build_image.sh",
        "tools/lib/lib.sh",
    ]

    @property
    def title(self):
        return f"Gradle {self.task_name} task"

    def get_gradle_command(self, extra_options=("--no-daemon", "--scan")) -> List:
        return (
            ["./gradlew"]
            + list(extra_options)
            + [f":airbyte-integrations:connectors:{self.context.connector.technical_name}:{self.task_name}"]
        )

    @property
    def connector_dir(self) -> Directory:
        return self.context.get_connector_dir(exclude=["secrets"])

    async def run_gradle_command(self, connector_under_test) -> StepResult:
        connector_under_test = connector_under_test.with_exec(self.get_gradle_command())
        return await self.get_step_result(connector_under_test)


class Test(GradleTask):
    task_name = "test"

    async def _run(self) -> StepResult:
        self.context.dagger_client = self.get_dagger_pipeline(self.context.dagger_client)

        connector_under_test = (await environments.with_gradle(self.context, self.BUILD_INCLUDE)).with_mounted_directory(
            str(self.context.connector.code_directory), self.connector_dir
        )

        return await self.run_gradle_command(connector_under_test)


class IntegrationTest(GradleTask):

    task_name = "integrationTest"

    async def _run(self) -> StepResult:
        self.context.dagger_client = self.get_dagger_pipeline(self.context.dagger_client)
        connector_java_build_cache = self.context.dagger_client.cache_volume("connector_java_build_cache")

        connector_under_test = (
            (await environments.with_gradle(self.context, self.BUILD_INCLUDE))
            .with_mounted_cache(
                f"/airbyte/airbyte-integrations/connectors/{self.context.connector.technical_name}/build", connector_java_build_cache
            )
            .with_mounted_directory(str(self.context.connector.code_directory), self.connector_dir)
            .with_env_variable("TESTCONTAINERS_RYUK_DISABLED", "true")
            .with_directory(f"{self.context.connector.code_directory}/secrets", self.context.secrets_dir)
        )

        return await self.run_gradle_command(connector_under_test)


async def run_all_tests(context: ConnectorTestContext) -> List[StepResult]:
    context.secrets_dir = await secrets.get_connector_secret_dir(context)
    return [await IntegrationTest(context).run()]
