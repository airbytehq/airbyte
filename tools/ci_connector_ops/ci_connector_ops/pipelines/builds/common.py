#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from abc import ABC

from ci_connector_ops.pipelines.bases import Step
from ci_connector_ops.pipelines.contexts import ConnectorTestContext


class BuildConnectorImageBase(Step, ABC):
    @property
    def title(self):
        return f"Build {self.context.connector.technical_name} docker image for platform {self.build_platform}"

    def __init__(self, context: ConnectorTestContext, build_platform) -> None:
        self.build_platform = build_platform
        super().__init__(context)
