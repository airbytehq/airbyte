#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Optional, Tuple

from ci_connector_ops.pipelines.bases import Step, StepResult, StepStatus
from dagger import Container, QueryError


class BuildConnectorImage(Step):
    """
    A step to build a Python connector image using its Dockerfile.
    A spec command is run on the container to validate it was built successfully.
    """

    title = "Build connector image"

    async def _run(self) -> Tuple[StepResult, Optional[Container]]:
        connector_dir = self.context.get_connector_dir()
        connector = connector_dir.docker_build()
        try:
            build_result = await self.get_step_result(connector.with_exec(["spec"]))
            return build_result, connector
        except QueryError as e:
            return StepResult(self, StepStatus.FAILURE, stderr=str(e)), None
