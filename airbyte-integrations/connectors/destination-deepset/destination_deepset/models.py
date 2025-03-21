# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import json
from enum import StrEnum, unique
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from airbyte_cdk.models import AirbyteRecordMessage
from destination_deepset import util


__all__ = [
    "DeepsetCloudConfig",
    "DeepsetCloudFile",
    "FileData",
    "Filetypes",
]


@unique
class Filetypes(StrEnum):
    """Available stream formats for Airbyte's source connectors"""

    AVRO = "avro"
    CSV = "csv"
    JSONL = "jsonl"
    PARQUET = "parquet"
    DOCUMENT = "unstructured"


class DeepsetCloudConfig(BaseModel):
    """Configuration for the deepset cloud destination."""

    model_config = ConfigDict(extra="allow")

    api_key: str = Field(title="API Key", description="Your deepset cloud API key", min_length=8)
    base_url: str = Field(
        default="https://api.cloud.deepset.ai",
        title="Base URL",
        description="Base url of your deepset cloud instance. Configure this if using an on-prem instance.",
    )
    workspace: str = Field(title="Workspace", description="Name of workspace to which to sync the data.")
    retries: int = Field(5, title="Retries", description="Number of times to retry an action before giving up.")


class FileData(BaseModel):
    """Data for a file to be synced to deepset cloud."""

    model_config = ConfigDict(extra="allow")

    content: str = Field(
        title="Content",
        description="Markdown formatted text extracted from Markdown, TXT, PDF, Word, Powerpoint or Google documents.",
    )
    document_key: str = Field(
        title="Document Key",
        description="A unique identifier for the processed file which can be used as a primary key.",
    )
    last_modified: str | None = Field(
        None,
        alias="_ab_source_file_last_modified",
        title="Last Modified",
        description="The last modified timestamp of the file.",
    )
    file_url: str | None = Field(
        None,
        alias="_ab_source_file_url",
        title="File URL",
        description="The fully qualified URL to the file on the remote server.",
    )
    file_parse_error: str | None = Field(
        None,
        alias="_ab_source_file_parse_error",
        title="File Parse Error",
        description="Error encountered while parsing the file.",
    )


class DeepsetCloudFile(BaseModel):
    name: str = Field(title="Name", description="File Name")
    content: bytes | str = Field(title="Content", description="File Content")
    meta: dict[str, Any] = Field(default_factory={}, title="Meta Data", description="File Meta Data")

    @property
    def meta_as_string(self) -> str:
        """Return metadata as a string."""
        return json.dumps(self.meta or {})

    @classmethod
    def from_record(cls, record: AirbyteRecordMessage) -> DeepsetCloudFile:
        data = FileData.model_validate(record.data)
        name = Path(util.generate_name(data.document_key, record.stream, namespace=record.namespace))

        return cls(
            name=f"{name.stem}.md",
            content=data.content,
            meta={
                "airbyte": {
                    "stream": record.stream,
                    "emitted_at": record.emitted_at,
                    **({"namespace": record.namespace} if record.namespace else {}),
                    **({"file_parse_error": data.file_parse_error} if data.file_parse_error else {}),
                },
                **({"source_file_extension": name.suffix} if name.suffix else {}),
                **data.model_dump(exclude={"content", "file_parse_error"}, exclude_none=True),
            },
        )
