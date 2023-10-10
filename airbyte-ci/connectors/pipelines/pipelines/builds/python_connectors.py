#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dagger import Container, Platform
from pipelines.actions.environments import with_airbyte_python_connector
from pipelines.bases import StepResult
from pipelines.builds.common import BuildConnectorImagesBase
from pipelines.contexts import ConnectorContext


class BuildConnectorImages(BuildConnectorImagesBase):
    """
    A step to build a Python connector image.
    A spec command is run on the container to validate it was built successfully.
    """

    async def _build_connector(self, platform: Platform) -> Container:
        return await with_airbyte_python_connector(self.context, platform)


async def run_connector_build(context: ConnectorContext) -> StepResult:
    return await BuildConnectorImages(context).run()
