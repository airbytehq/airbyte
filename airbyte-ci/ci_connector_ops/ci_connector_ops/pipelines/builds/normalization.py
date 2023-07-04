#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.pipelines.bases import Step, StepResult, StepStatus
from ci_connector_ops.pipelines.contexts import ConnectorContext


# TODO this class could be deleted
# if java connectors tests are not relying on an existing local normalization image to run
class BuildOrPullNormalization(Step):
    """A step to build or pull the normalization image for a connector according to the image name."""

    def __init__(self, context: ConnectorContext, normalization_image: str) -> None:
        """Initialize the step to build or pull the normalization image.

        Args:
            context (ConnectorContext): The current connector context.
            normalization_image (str): The normalization image to build (if :dev) or pull.
        """
        super().__init__(context)
        self.use_dev_normalization = normalization_image.endswith(":dev")
        self.normalization_image = normalization_image
        self.title = f"Build {self.normalization_image}" if self.use_dev_normalization else f"Pull {self.normalization_image}"

    async def _run(self) -> StepResult:
        if self.use_dev_normalization:
            build_normalization_container = environments.with_normalization(self.context)
        else:
            build_normalization_container = self.context.dagger_client.container().from_(self.normalization_image)
        return StepResult(self, StepStatus.SUCCESS, output_artifact=build_normalization_container)
