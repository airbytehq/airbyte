from dataclasses import dataclass
from typing import Any, List, Mapping, Optional

from airbyte_cdk.sources.file_based.exceptions import ConfigValidationError
from airbyte_cdk.sources.file_based.remote_file import FileType


MAX_N_FILES_FOR_STREAM_SCHEMA_INFERENCE = 10


@dataclass
class FileBasedStreamConfig:
    """
    Validated configuration for a file-based stream.
    """

    name: str
    file_type: FileType
    globs: List[str]
    catalog_schema: Optional[Mapping[str, Any]]
    input_schema: Optional[Mapping[str, Any]]
    primary_key: Optional[str]
    validation_policy: str

    @classmethod
    def from_raw_config(cls, raw_config: Mapping[str, Any]) -> "FileBasedStreamConfig":
        try:
            file_type = FileType(raw_config["file_type"])
        except ValueError:
            raise ConfigValidationError(f"Invalid file type: {raw_config['file_type']}")

        globs = raw_config["globs"]

        return FileBasedStreamConfig(
            name=raw_config["name"],
            file_type=file_type,
            globs=globs,
            catalog_schema=raw_config.get("json_schema"),
            input_schema=raw_config.get("input_schema"),
            primary_key=raw_config.get("primary_key"),
            validation_policy=raw_config["validation_policy"],
        )
