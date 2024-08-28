# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import dagger
from pipelines.consts import GCS_PUBLIC_DOMAIN
from pipelines.dagger.actions import remote_storage
from pipelines.models.secrets import Secret


@dataclass(kw_only=True)
class Artifact:
    """A dataclass to represent an artifact produced by a pipeline execution."""

    name: str
    content_type: str
    content: dagger.File
    to_upload: bool = True
    local_path: Optional[Path] = None
    gcs_url: Optional[str] = None

    async def save_to_local_path(self, path: Path) -> Path:
        exported = await self.content.export(str(path))
        if exported:
            self.local_path = path
            return path
        else:
            raise Exception(f"Failed to save artifact {self.name} to local path {path}")

    async def upload_to_gcs(self, dagger_client: dagger.Client, bucket: str, key: str, gcs_credentials: Secret) -> str:
        gcs_cp_flags = [f'--content-disposition=filename="{self.name}"']
        if self.content_type is not None:
            gcs_cp_flags = gcs_cp_flags + [f"--content-type={self.content_type}"]

        report_upload_exit_code, _, _ = await remote_storage.upload_to_gcs(
            dagger_client=dagger_client,
            file_to_upload=self.content,
            key=key,
            bucket=bucket,
            gcs_credentials=gcs_credentials,
            flags=gcs_cp_flags,
        )
        if report_upload_exit_code != 0:
            raise Exception(f"Failed to upload artifact {self.name} to GCS. Exit code: {report_upload_exit_code}.")
        self.gcs_url = f"{GCS_PUBLIC_DOMAIN}/{bucket}/{key}"
        return f"{GCS_PUBLIC_DOMAIN}/{bucket}/{key}"
