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
    JAVA_BUILD_INCLUDE = [
        "airbyte-api",
        "airbyte-commons-cli",
        "airbyte-commons-protocol",
        "airbyte-commons",
        "airbyte-config",
        "airbyte-connector-test-harnesses",
        "airbyte-db",
        "airbyte-integrations/bases",
        "airbyte-json-validation",
        "airbyte-protocol",
        "airbyte-test-utils",
        "buildSrc",
        "tools/bin/build_image.sh",
        "tools/lib/lib.sh",
    ]

    SOURCE_BUILD_INCLUDE = [
        "airbyte-integrations/connectors/source-jdbc",
        "airbyte-integrations/connectors/source-relational-db",
    ]

    DESTINATION_BUILD_INCLUDE = []

    @property
    def build_include(self):
        if self.context.connector.connector_type == "source":
            return self.JAVA_BUILD_INCLUDE + self.SOURCE_BUILD_INCLUDE
        else:
            return self.JAVA_BUILD_INCLUDE + self.DESTINATION_BUILD_INCLUDE

    @property
    def title(self):
        return f"Gradle {self.task_name} task"

    async def get_patched_connector_dir(self) -> Directory:
        """Removes the airbyte-connector-acceptance-test plugin import from build.gradle

        Returns:
            Directory: The patched connector directory
        """
        gradle_file_content = await self.context.get_connector_dir(include=["build.gradle"]).file("build.gradle").contents()
        patched_file_content = ""
        for line in gradle_file_content.split("\n"):
            if "id 'airbyte-connector-acceptance-test'" not in line:
                patched_file_content += line + "\n"
        return self.context.get_connector_dir(exclude=["build", "secrets"]).with_new_file("build.gradle", patched_file_content)

    def get_gradle_command(self, extra_options=("--no-daemon", "--scan")) -> List:
        return (
            ["./gradlew", "--no-watch-fs"]
            + list(extra_options)
            + [f":airbyte-integrations:connectors:{self.context.connector.technical_name}:{self.task_name}"]
        )

    async def run_gradle_command(self, connector_under_test) -> StepResult:
        connector_under_test = connector_under_test.with_exec(self.get_gradle_command())
        return await self.get_step_result(connector_under_test)


class Test(GradleTask):
    task_name = "test"

    async def _run(self) -> StepResult:
        self.context.dagger_client = self.get_dagger_pipeline(self.context.dagger_client)

        connector_under_test = (await environments.with_gradle(self.context, self.build_include)).with_mounted_directory(
            str(self.context.connector.code_directory), await self.get_patched_connector_dir()
        )

        return await self.run_gradle_command(connector_under_test)


class IntegrationTestJava(GradleTask):

    task_name = "integrationTestJava"

    async def _run(self) -> StepResult:
        self.context.dagger_client = self.get_dagger_pipeline(self.context.dagger_client)
        connector_java_build_cache = self.context.dagger_client.cache_volume("connector_java_build_cache")

        connector_under_test = (
            environments.with_gradle(self.context, self.build_include)
            .with_mounted_cache(f"{self.context.connector.code_directory}/build", connector_java_build_cache)
            .with_mounted_directory(str(self.context.connector.code_directory), await self.get_patched_connector_dir())
            .with_env_variable("TESTCONTAINERS_RYUK_DISABLED", "true")
            .with_directory(f"{self.context.connector.code_directory}/secrets", self.context.secrets_dir)
        )

        return await self.run_gradle_command(connector_under_test)


async def run_all_tests(context: ConnectorTestContext) -> List[StepResult]:
    context.secrets_dir = await secrets.get_connector_secret_dir(context)
    return [await IntegrationTestJava(context).run()]
    # return [await IntegrationTest(context).run()]
