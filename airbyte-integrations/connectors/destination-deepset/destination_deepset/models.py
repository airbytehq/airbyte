# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import json
from enum import Enum, unique
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from airbyte_cdk.models import AirbyteRecordMessage, DestinationSyncMode


__all__ = [
    "DeepsetCloudConfig",
    "DeepsetCloudFile",
    "WriteMode",
]

SUPPORTED_FILE_EXTENSIONS = [
    ".csv",
    ".docx",
    ".html",
    ".json",
    ".md",
    ".txt",
    ".pdf",
    ".pptx",
    ".xlsx",
    ".xml",
]


@unique
class WriteMode(str, Enum):
    FAIL = "FAIL"
    KEEP = "KEEP"
    OVERWRITE = "OVERWRITE"

    @classmethod
    def from_destination_sync_mode(cls, destination_sync_mode: DestinationSyncMode) -> WriteMode:
        return SUPPORTED_DESTINATION_SYNC_MODES.get(destination_sync_mode, FALLBACK_FILE_WRITE_MODE)


FALLBACK_FILE_WRITE_MODE = WriteMode.KEEP

SUPPORTED_DESTINATION_SYNC_MODES = {
    DestinationSyncMode.append: WriteMode.KEEP,
    DestinationSyncMode.overwrite: WriteMode.OVERWRITE,
}


class DeepsetCloudConfig(BaseModel):
    api_key: str = Field(title="API Key", description="Your deepset cloud API key")
    base_url: str = Field(
        default="https://api.cloud.deepset.ai/",
        title="Base URL",
        description="Base url of your deepset cloud instance. Configure this if using an on-prem instance.",
    )
    workspace: str = Field(title="Workspace", description="Name of workspace to which to sync the data.")
    retries: int = Field(10, title="Retries", description="Number of times to retry an action before giving up.")


class DeepsetCloudFile(BaseModel):
    name: str = Field(title="Name", description="File Name")
    content: str | bytes = Field(title="Content", description="File Content")
    meta: dict[str, Any] = Field(default_factory={}, title="Meta Data", description="File Meta Data")

    @property
    def extension(self) -> str:
        return Path(self.name).suffix

    @property
    def meta_as_string(self) -> str:
        """Return metadata as a string."""
        return json.dumps(self.meta or {})

    @classmethod
    def from_message(cls, message: AirbyteRecordMessage) -> DeepsetCloudFile:
        # @todo[abraham]: implement me!
        pass
