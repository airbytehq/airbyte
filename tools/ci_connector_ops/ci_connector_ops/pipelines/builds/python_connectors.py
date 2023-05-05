#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from ci_connector_ops.pipelines.actions.environments import with_airbyte_python_connector
from ci_connector_ops.pipelines.bases import StepResult, StepStatus
from ci_connector_ops.pipelines.builds.common import BuildConnectorImageBase
from dagger import QueryError


class BuildConnectorImage(BuildConnectorImageBase):
    """
    A step to build a Python connector image.
    A spec command is run on the container to validate it was built successfully.
    """

    async def _run(self) -> StepResult:
        connector = with_airbyte_python_connector(self.context, self.build_platform)
        try:
            return await self.get_step_result(connector.with_exec(["spec"]))
        except QueryError as e:
            return StepResult(self, StepStatus.FAILURE, stderr=str(e))
