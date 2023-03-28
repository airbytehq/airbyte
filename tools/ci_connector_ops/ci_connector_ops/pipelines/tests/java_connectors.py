#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups steps made to run tests for a specific Java connector given a test context."""

from abc import ABC
from typing import ClassVar, List

from ci_connector_ops.pipelines.actions import environments, secrets
from ci_connector_ops.pipelines.bases import Step, StepResult
from ci_connector_ops.pipelines.contexts import ConnectorTestContext


class GradleTask(Step, ABC):
    task_name: ClassVar
    build_include: ClassVar
    mount_secrets: bool = False

    async def run(self) -> StepResult:
        self.context.dagger_client = self.get_dagger_pipeline(self.context.dagger_client)

        connector_under_test = (
            (await environments.with_gradle(self.context, self.build_include))
            .with_unix_socket("/var/run/docker.sock", self.context.dagger_client.host().unix_socket("/var/run/docker.sock"))
            .with_env_variable("TESTCONTAINERS_HOST_OVERRIDE", "host.docker.internal")
            .with_mounted_directory(str(self.context.connector.code_directory), self.context.get_connector_dir(exclude=["secrets"]))
        )

        if self.mount_secrets:
            connector_under_test = connector_under_test.with_directory(
                f"{self.context.connector.code_directory}/secrets", self.context.secrets_dir
            )

        connector_under_test = connector_under_test.with_exec(
            [
                "./gradlew",
                "--no-daemon",
                "--scan",
                f":airbyte-integrations:connectors:{self.context.connector.technical_name}:{self.task_name}",
            ]
        )

        return await self.get_step_result(connector_under_test)


class IntegrationTests(GradleTask):

    title = "Gradle integrationTest task"
    task_name = "integrationTest"
    build_include = [
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
    mount_secrets = True


async def run_all_tests(context: ConnectorTestContext) -> List[StepResult]:
    context.secrets_dir = await secrets.get_connector_secret_dir(context)
    connector_install_results = await IntegrationTests(context).run()
    return [connector_install_results]
