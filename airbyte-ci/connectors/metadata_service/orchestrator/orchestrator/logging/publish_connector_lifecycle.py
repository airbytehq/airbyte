#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
from enum import Enum

from dagster import OpExecutionContext
from orchestrator.ops.slack import send_slack_message


class StageStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"

    def __str__(self) -> str:
        # convert to upper case
        return self.value.replace("_", " ").upper()

    def to_emoji(self) -> str:
        if self == StageStatus.IN_PROGRESS:
            return "🟡"
        elif self == StageStatus.SUCCESS:
            return "🟢"
        elif self == StageStatus.FAILED:
            return "🔴"
        else:
            return ""


class PublishConnectorLifecycleStage(str, Enum):
    METADATA_SENSOR = "metadata_sensor"
    METADATA_VALIDATION = "metadata_validation"
    REGISTRY_ENTRY_GENERATION = "registry_entry_generation"
    REGISTRY_GENERATION = "registry_generation"

    def __str__(self) -> str:
        # convert to title case
        return self.value.replace("_", " ").title()


class PublishConnectorLifecycle:
    """
    This class is used to log the lifecycle of a publishing a connector to the registries.

    It is used to log to the logger and slack (if enabled).

    This is nessesary as this lifecycle is not a single job, asset, resource, schedule, or sensor.
    """

    @staticmethod
    def stage_to_log_level(stage_status: StageStatus) -> str:
        if stage_status == StageStatus.FAILED:
            return "error"
        else:
            return "info"

    @staticmethod
    def create_log_message(
        lifecycle_stage: PublishConnectorLifecycleStage,
        stage_status: StageStatus,
        message: str,
    ) -> str:
        emoji = stage_status.to_emoji()
        return f"*{emoji} _{lifecycle_stage}_ {stage_status}*: {message}"

    @staticmethod
    def log(context: OpExecutionContext, lifecycle_stage: PublishConnectorLifecycleStage, stage_status: StageStatus, message: str):
        """Publish a connector notification log to logger and slack (if enabled)."""
        message = PublishConnectorLifecycle.create_log_message(lifecycle_stage, stage_status, message)

        level = PublishConnectorLifecycle.stage_to_log_level(stage_status)
        log_method = getattr(context.log, level)
        log_method(message)
        channel = os.getenv("PUBLISH_UPDATE_CHANNEL")
        if channel:
            slack_message = f"🤖 {message}"
            send_slack_message(context, channel, slack_message)
