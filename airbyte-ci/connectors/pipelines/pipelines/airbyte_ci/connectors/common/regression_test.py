#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import dagger
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.models.steps import Step, StepResult, StepStatus


class RegressionTest(Step):
    """Run the regression test for the connector.
    We test that:
    - The connector spec command successfully.

    Only works for poetry connectors.

    Example usage:

    steps_to_run.append(
        [StepToRun(id=CONNECTOR_TEST_STEP_ID.BUILD, step=BuildConnectorImages(context), depends_on=[CONNECTOR_TEST_STEP_ID.UPDATE_POETRY])]
    )

    steps_to_run.append(
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.REGRESSION_TEST,
                step=RegressionTest(context),
                depends_on=[CONNECTOR_TEST_STEP_ID.BUILD],
                args=lambda results: {"new_connector_container": results[CONNECTOR_TEST_STEP_ID.BUILD].output[LOCAL_BUILD_PLATFORM]},
            )
        ]
    )

    """

    context: ConnectorContext

    title = "Run regression test"

    async def _run(self, new_connector_container: dagger.Container) -> StepResult:
        try:
            await new_connector_container.with_exec(["spec"])
            await new_connector_container.with_mounted_file(
                "pyproject.toml", (await self.context.get_connector_dir(include=["pyproject.toml"])).file("pyproject.toml")
            ).with_exec(["poetry", "run", self.context.connector.technical_name, "spec"], skip_entrypoint=True)
        except dagger.ExecError as e:
            return StepResult(
                step=self,
                status=StepStatus.FAILURE,
                stderr=str(e),
            )
        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
        )
