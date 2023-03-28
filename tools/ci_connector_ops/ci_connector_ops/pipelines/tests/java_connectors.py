#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups steps made to run tests for a specific Java connector given a test context."""

from abc import ABC
from typing import ClassVar, List

import asyncer
from ci_connector_ops.pipelines.actions import environments, secrets
from ci_connector_ops.pipelines.bases import Step, StepResult, StepStatus
from ci_connector_ops.pipelines.contexts import ConnectorTestContext
from ci_connector_ops.pipelines.tests.common import AcceptanceTests
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

    @property
    def gradle_command(self) -> List:
        return [
            "./gradlew",
            "--no-daemon",
            "--scan",
            f":airbyte-integrations:connectors:{self.context.connector.technical_name}:{self.task_name}",
        ]

    @property
    def connector_dir(self) -> Directory:
        return self.context.get_connector_dir(exclude=["secrets"])

    async def run_gradle_command(self, connector_under_test) -> StepResult:
        connector_under_test = connector_under_test.with_exec(self.gradle_command)
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

    # @property
    # async def connector_dir(self) -> Directory:
    #     connector_dir = self.context.get_connector_dir(exclude=["secrets"])
    #     # We don't want to run connector acceptance test suite with Gradle
    #     # Stripping out the plugin declaration from the connector build.gradle file does that
    #     build_gradle_file_content = await connector_dir.file("build.gradle").contents()
    #     new_gradle_file = ""
    #     for line in build_gradle_file_content.split("\n"):
    #         if not "id 'airbyte-connector-acceptance-test'" in line:
    #             new_gradle_file += line + "\n"

    #     return connector_dir.with_new_file("build.gradle", new_gradle_file)

    async def _run(self) -> StepResult:
        self.context.dagger_client = self.get_dagger_pipeline(self.context.dagger_client)

        connector_under_test = (
            (await environments.with_gradle(self.context, self.BUILD_INCLUDE))
            # .with_env_variable("TESTCONTAINERS_HOST_OVERRIDE", "host.docker.internal")
            .with_mounted_directory(str(self.context.connector.code_directory), self.connector_dir)
        )

        connector_under_test = connector_under_test.with_directory(
            f"{self.context.connector.code_directory}/secrets", self.context.secrets_dir
        )

        return await self.run_gradle_command(connector_under_test)


async def run_all_tests(context: ConnectorTestContext) -> List[StepResult]:
    test_result = await Test(context).run()
    if test_result.status is StepStatus.FAILURE:
        return [test_result, IntegrationTest(context).skip()]

    context.secrets_dir = await secrets.get_connector_secret_dir(context)
    async with asyncer.create_task_group() as task_group:
        tasks = [
            task_group.soonify(IntegrationTest(context).run)(),
            # task_group.soonify(AcceptanceTests(context).run)(),
        ]
    return [test_result] + [task.value for task in tasks]
