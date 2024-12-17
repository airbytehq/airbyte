# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import json
from enum import Enum, unique
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import unquote, urlparse

from airbyte_cdk.models import AirbyteRecordMessage
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from datetime import datetime


__all__ = [
    "DeepsetCloudConfig",
    "DeepsetCloudFile",
    "FileData",
    "Filetypes",
    "SUPPORTED_FILE_EXTENSIONS",
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
class Filetypes(str, Enum):
    """Available stream formats for Airbyte's source connectors"""

    AVRO = "avro"
    CSV = "csv"
    JSONL = "jsonl"
    PARQUET = "parquet"
    DOCUMENT = "unstructured"


class DeepsetCloudConfig(BaseModel):
    api_key: str = Field(title="API Key", description="Your deepset cloud API key")
    base_url: str = Field(
        default="https://api.cloud.deepset.ai/",
        title="Base URL",
        description="Base url of your deepset cloud instance. Configure this if using an on-prem instance.",
    )
    workspace: str = Field(title="Workspace", description="Name of workspace to which to sync the data.")
    retries: int = Field(5, title="Retries", description="Number of times to retry an action before giving up.")


class FileData(BaseModel):
    content: str = Field(
        title="Content",
        description="Markdown formatted text extracted from Markdown, TXT, PDF, Word, Powerpoint or Google documents.",
    )
    document_key: str = Field(
        title="Document Key",
        description="A unique identifier for the processed file which can be used as a primary key.",
    )
    last_modified: datetime | None = Field(
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

    @property
    def name(self) -> str:
        """Generate a name from the document key.

        Returns:
            str: The unique name of the document.
        """
        # Parse URL and get path segments
        parsed = urlparse(self.document_key)
        path_segments = parsed.path.strip("/").split("/")

        # Join segments with underscores to create filename
        filename = "_".join(path_segments)

        # URL decode the filename to handle special characters
        return unquote(filename)

    @property
    def filename(self) -> str:
        """The name of the file with Markdown extension.

        Returns:
            str: The unique file name with Markdown extension.
        """
        return Path(self.name).stem + ".md"


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
    def from_record(cls, record: AirbyteRecordMessage) -> DeepsetCloudFile:
        data = FileData.parse_obj(record.data)
        return cls(
            name=data.filename,
            content=data.content,
            meta={
                "airbyte": {
                    "stream": record.stream,
                    "emitted_at": record.emitted_at,
                    **({"namespace": record.namespace} if record.namespace else {}),
                    **({"file_parse_error": data.file_parse_error} if data.file_parse_error else {}),
                },
                "source_file_extension": Path(data.name).suffix,
                **data.dict(exclude={"content", "file_parse_error"}, exclude_none=True),
            },
        )
