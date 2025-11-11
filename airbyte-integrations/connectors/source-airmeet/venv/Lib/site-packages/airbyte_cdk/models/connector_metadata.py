"""Models to represent the structure of a `metadata.yaml` file."""

from __future__ import annotations

from enum import Enum
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class ConnectorLanguage(str, Enum):
    """Connector implementation language."""

    PYTHON = "python"
    JAVA = "java"
    LOW_CODE = "low-code"
    MANIFEST_ONLY = "manifest-only"
    UNKNOWN = "unknown"


class ConnectorBuildOptions(BaseModel):
    """Connector build options from metadata.yaml."""

    model_config = {"extra": "allow"}

    baseImage: str | None = Field(
        None,
        description="Base image to use for building the connector",
    )
    path: str | None = Field(
        None,
        description="Path to the connector code within the repository",
    )


class SuggestedStreams(BaseModel):
    """Suggested streams from metadata.yaml."""

    streams: list[str] = Field(
        default=[],
        description="List of suggested streams for the connector",
    )


class ConnectorMetadata(BaseModel):
    """Connector metadata from metadata.yaml."""

    model_config = {"extra": "allow"}

    dockerRepository: str = Field(..., description="Docker repository for the connector image")
    dockerImageTag: str = Field(..., description="Docker image tag for the connector")

    tags: list[str] = Field(
        default=[],
        description="List of tags for the connector",
    )

    suggestedStreams: SuggestedStreams | None = Field(
        default=None,
        description="Suggested streams for the connector",
    )

    @property
    def language(self) -> ConnectorLanguage:
        """Get the connector language."""
        for tag in self.tags:
            if tag.startswith("language:"):
                language = tag.split(":", 1)[1]
                if language == "python":
                    return ConnectorLanguage.PYTHON
                elif language == "java":
                    return ConnectorLanguage.JAVA
                elif language == "low-code":
                    return ConnectorLanguage.LOW_CODE
                elif language == "manifest-only":
                    return ConnectorLanguage.MANIFEST_ONLY

        return ConnectorLanguage.UNKNOWN

    connectorBuildOptions: ConnectorBuildOptions | None = Field(
        None, description="Options for building the connector"
    )


class MetadataFile(BaseModel):
    """Represents the structure of a metadata.yaml file."""

    model_config = {"extra": "allow"}

    data: ConnectorMetadata = Field(..., description="Connector metadata")

    @classmethod
    def from_file(
        cls,
        file_path: Path,
    ) -> MetadataFile:
        """Load metadata from a YAML file."""
        if not file_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {file_path!s}")

        metadata_content = file_path.read_text()
        metadata_dict = yaml.safe_load(metadata_content)

        if not metadata_dict or "data" not in metadata_dict:
            raise ValueError(
                "Invalid metadata format: missing 'data' field in YAML file '{file_path!s}'"
            )

        metadata_file = MetadataFile.model_validate(metadata_dict)
        return metadata_file
