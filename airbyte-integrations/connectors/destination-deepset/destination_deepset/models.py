from __future__ import annotations

from enum import Enum, unique

from deepset_cloud_sdk.models import DeepsetCloudFileBytes as DeepsetCloudFileBytesBase
from pydantic import BaseModel, Field

from airbyte_cdk.models import AirbyteMessage


__all__ = [
    "DeepsetConfig",
    "DeepsetCloudFileBytes",
    "WriteMode",
]


@unique
class WriteMode(str, Enum):
    FAIL = "FAIL"
    KEEP = "KEEP"
    OVERWRITE = "OVERWRITE"


class DeepsetConfig(BaseModel):
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


class DeepsetCloudFileBytes(DeepsetCloudFileBytesBase):
    @classmethod
    def from_message(cls, message: AirbyteMessage) -> DeepsetCloudFileBytes:
        # @todo[abraham]: implement me!
        pass
