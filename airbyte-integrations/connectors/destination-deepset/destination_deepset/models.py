# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import json
from enum import Enum, unique
from pathlib import Path
from typing import Any, Dict, Union
from pydantic import BaseModel, Field
from airbyte_cdk.models import AirbyteRecordMessage

__all__ = [
    "DeepsetCloudConfig",
    "DeepsetCloudFile",
    "WriteMode",
]

SUPPORTED_FILE_EXTENSIONS = [".csv", ".docx", ".html", ".json", ".md", ".txt", ".pdf", ".pptx", ".xlsx", ".xml",]
@unique
class WriteMode(str, Enum):
    FAIL = "FAIL"
    KEEP = "KEEP"
    OVERWRITE = "OVERWRITE"

class DeepsetCloudConfig(BaseModel):
    api_key: str = Field(title="API Key", description="Your deepset cloud API key")
    base_url: str = Field(
        default="https://api.cloud.deepset.ai/",
        title="Base URL",
        description="Base url of your deepset cloud instance. Configure this if using an on-prem instance.",
    )
    workspace: str = Field(title="Workspace", description="Name of workspace to which to sync the data.")
    write_mode: WriteMode = Field(
        default=WriteMode.KEEP,
        title="Write Mode",
        description="Specifies what to do when a file with the same name already exists in the workspace.",
    )
    sync: bool = Field(
        default=True,
        title="Sync",
        description="Ensure that the files have been saved and are visible in deepset cloud.",
    )
    retries: int = Field(10, title='Retries', description='Number of times to retry an action before giving up.')


class DeepsetCloudFile(BaseModel):
    name: str = Field(title="Name", description="File Name")
    content: Union[str, bytes] = Field(title="Content", description="File Content")
    meta: Dict[str, Any] = Field(default_factory={}, title="Meta Data", description="File Meta Data")

    @property
    def extension(self) -> str:
        return Path(self.name).suffix

    @property
    def meta_as_string(self) -> str:
        """Return metadata as a string."""
        return json.dumps(self.meta or {})

    @classmethod
    def from_message(cls, message: AirbyteRecordMessage)-> DeepsetCloudFile
        # @todo[abraham]: implement me!
        pass
