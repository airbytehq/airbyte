#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Optional, Tuple

from ci_connector_ops.pipelines.bases import StepResult, StepStatus
from ci_connector_ops.pipelines.builds.common import BuildConnectorImageBase
from dagger import Container, QueryError


class BuildConnectorImage(BuildConnectorImageBase):
    """
    A step to build a Python connector image using its Dockerfile.
    A spec command is run on the container to validate it was built successfully.
    """

    async def _run(self) -> Tuple[StepResult, Optional[Container]]:
        connector_dir = self.context.get_connector_dir()
        connector = connector_dir.docker_build(platform=self.build_platform)
        try:
            build_result = await self.get_step_result(connector.with_exec(["spec"]))
            return build_result, connector
        except QueryError as e:
            return StepResult(self, StepStatus.FAILURE, stderr=str(e)), None
