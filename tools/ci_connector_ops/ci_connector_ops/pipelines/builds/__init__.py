#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""This module groups factory like functions to dispatch builds steps according to the connector language."""

from typing import Optional, Tuple

from ci_connector_ops.pipelines.bases import StepResult
from ci_connector_ops.pipelines.builds import java_connectors, python_connectors
from ci_connector_ops.pipelines.contexts import ConnectorTestContext
from ci_connector_ops.utils import ConnectorLanguage
from dagger import Container

BUILD_ARCHITECTURES = ["linux/amd64", "linux/arm64"]

LANGUAGE_MAPPING = {
    "build_connector_image": {
        ConnectorLanguage.PYTHON: python_connectors.BuildConnectorImage,
        ConnectorLanguage.LOW_CODE: python_connectors.BuildConnectorImage,
        ConnectorLanguage.JAVA: java_connectors.BuildConnectorImage,
    },
}


async def run_connector_build(context: ConnectorTestContext) -> Tuple[StepResult, Optional[Container]]:
    """Build a connector according to its language and return the build result and the built container.

    Args:
        context (ConnectorTestContext): The current connector test context.

    Returns:
        List[StepResult]: The results of the build steps.
    """
    if BuildConnectorImage := LANGUAGE_MAPPING["build_connector_image"].get(context.connector.language):
        return await BuildConnectorImage(context).run()
    else:
        context.logger.warning(f"No tests defined for connector language {context.connector.language}!")
        return BuildConnectorImage(context).skip(), None
