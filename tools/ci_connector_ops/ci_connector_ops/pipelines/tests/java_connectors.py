#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import List

from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.pipelines.bases import Step, StepResult
from ci_connector_ops.pipelines.contexts import ConnectorTestContext


class IntegrationTests(Step):

    title = "Gradle test task"

    CONNECTOR_BUILD_INCLUDE = [
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

    async def run(self) -> StepResult:
        self.context.dagger_client = self.get_dagger_pipeline(self.context.dagger_client)

        connector_under_test = (
            (await environments.with_gradle(self.context, self.CONNECTOR_BUILD_INCLUDE))
            .with_unix_socket("/var/run/docker.sock", self.context.dagger_client.host().unix_socket("/var/run/docker.sock"))
            .with_env_variable("TESTCONTAINERS_HOST_OVERRIDE", "host.docker.internal")
            .with_env_variable("CI", "true")
            .with_mounted_directory(str(self.context.connector.code_directory), self.context.get_connector_dir())
            .with_exec(
                [
                    "./gradlew",
                    "--no-daemon",
                    "--scan",
                    f":airbyte-integrations:connectors:{self.context.connector.technical_name}:integrationTest",
                ]
            )
        )

        return await self.get_step_result(connector_under_test)


async def run_all_tests(context: ConnectorTestContext) -> List[StepResult]:
    connector_install_results = await IntegrationTests(context).run()
    return [connector_install_results]
