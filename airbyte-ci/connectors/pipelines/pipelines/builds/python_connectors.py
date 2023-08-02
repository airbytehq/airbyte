#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pipelines.actions.environments import with_airbyte_python_connector
from pipelines.bases import StepResult, StepStatus
from pipelines.builds.common import BuildConnectorImageBase, BuildConnectorImageForAllPlatformsBase
from pipelines.contexts import ConnectorContext
from dagger import QueryError


class BuildConnectorImage(BuildConnectorImageBase):
    """
    A step to build a Python connector image.
    A spec command is run on the container to validate it was built successfully.
    """

    async def _run(self) -> StepResult:
        connector = await with_airbyte_python_connector(self.context, self.build_platform)
        try:
            return await self.get_step_result(connector.with_exec(["spec"]))
        except QueryError as e:
            return StepResult(self, StepStatus.FAILURE, stderr=str(e))


class BuildConnectorImageForAllPlatforms(BuildConnectorImageForAllPlatformsBase):
    """Build a Python connector image for all platforms."""

    async def _run(self) -> StepResult:
        build_results_per_platform = {}
        for platform in self.ALL_PLATFORMS:
            build_connector_step_result = await BuildConnectorImage(self.context, platform).run()
            if build_connector_step_result.status is not StepStatus.SUCCESS:
                return build_connector_step_result
            build_results_per_platform[platform] = build_connector_step_result.output_artifact
        return self.get_success_result(build_results_per_platform)


async def run_connector_build(context: ConnectorContext) -> StepResult:
    return await BuildConnectorImageForAllPlatforms(context).run()
