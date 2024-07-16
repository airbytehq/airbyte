# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from connector_ops.utils import Connector  # type: ignore
from google.cloud import storage  # type: ignore

if TYPE_CHECKING:
    from typing import Any


@dataclass
class FileToPersist:
    file_name: str
    file_content: str | None = None

    def set_file_content(self, file_content: str) -> None:
        self.file_content = file_content


class ResultBackend(ABC):
    def __init__(self, *args: Any, **kwargs: Any):
        self.logger = logging.getLogger(self.__class__.__name__)

    def write(self, connector: Connector, file_to_persist: FileToPersist) -> None:
        if not file_to_persist.file_content:
            raise ValueError("File content must be set before writing to local directory")
        self._write(connector, file_to_persist)

    @abstractmethod
    def _write(self, connector: Connector, file_to_persist: FileToPersist) -> None:
        raise NotImplementedError("write method must be implemented by subclass")

    @abstractmethod
    def artifact_already_exists(self, connector: Connector, file_to_persist: FileToPersist) -> bool:
        raise NotImplementedError("insights_already_exist method must be implemented by subclass")


class LocalDir(ResultBackend):
    def __init__(self, local_directory: Path):
        super().__init__()
        if not local_directory.exists():
            local_directory.mkdir(parents=True)

        self.local_directory = local_directory

    def _write(self, connector: Connector, file_to_persist: FileToPersist) -> None:
        assert file_to_persist.file_content is not None
        connector_result_directory = self.local_directory / connector.technical_name / connector.version
        connector_result_directory.mkdir(parents=True, exist_ok=True)
        file_path = connector_result_directory / file_to_persist.file_name
        with open(file_path, "w") as f:
            f.write(file_to_persist.file_content)
            self.logger.info(f"{file_to_persist.file_name} written to {file_path}")

    def artifact_already_exists(self, connector: Connector, file_to_persist: FileToPersist) -> bool:
        connector_result_directory = self.local_directory / connector.technical_name / connector.version
        return (connector_result_directory / file_to_persist.file_name).exists()


class GCSBucket(ResultBackend):

    DEFAULT_GCP_PROJECT = "prod-ab-cloud-proj"

    def __init__(self, bucket_name: str, key_prefix: str, gcp_project: str = DEFAULT_GCP_PROJECT):
        super().__init__()
        self.bucket_name = bucket_name
        self.key_prefix = key_prefix
        self.storage_client = storage.Client(project=gcp_project)
        self.bucket = self.storage_client.bucket(self.bucket_name)

    def _write(self, connector: Connector, file_to_persist: FileToPersist) -> None:
        assert file_to_persist.file_content is not None
        version_blob_prefix = f"{self.key_prefix}/{connector.technical_name}/{connector.version}"
        latest_blob_prefix = f"{self.key_prefix}/{connector.technical_name}/latest"
        for blob_prefix in [version_blob_prefix, latest_blob_prefix]:
            blob = self.bucket.blob(f"{blob_prefix}/{file_to_persist.file_name}")
            blob.upload_from_string(file_to_persist.file_content)
            self.logger.info(f"{file_to_persist.file_name} written to {blob.public_url}")

    def artifact_already_exists(self, connector: Connector, file_to_persist: FileToPersist) -> bool:
        blob_prefix = f"{self.key_prefix}/{connector.technical_name}/{connector.version}"
        return self.bucket.blob(f"{blob_prefix}/{file_to_persist.file_name}").exists()
