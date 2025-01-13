#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dagger import Platform

from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.dagger.actions.connector import normalization
from pipelines.models.steps import Step, StepResult, StepStatus


# TODO this class could be deleted
# if java connectors tests are not relying on an existing local normalization image to run
class BuildOrPullNormalization(Step):
    """A step to build or pull the normalization image for a connector according to the image name."""

    context: ConnectorContext

    def __init__(self, context: ConnectorContext, normalization_image: str, build_platform: Platform) -> None:
        """Initialize the step to build or pull the normalization image.

        Args:
            context (ConnectorContext): The current connector context.
            normalization_image (str): The normalization image to build (if :dev) or pull.
        """
        super().__init__(context)
        self.build_platform = build_platform
        self.use_dev_normalization = normalization_image.endswith(":dev")
        self.normalization_image = normalization_image

    @property
    def title(self) -> str:
        return f"Build {self.normalization_image}" if self.use_dev_normalization else f"Pull {self.normalization_image}"

    async def _run(self) -> StepResult:
        if self.use_dev_normalization:
            build_normalization_container = normalization.with_normalization(self.context, self.build_platform)
        else:
            build_normalization_container = self.context.dagger_client.container().from_(self.normalization_image)
        return StepResult(step=self, status=StepStatus.SUCCESS, output=build_normalization_container)
