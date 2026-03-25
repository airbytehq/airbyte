# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import io
import logging
import os
import tempfile
import zipfile
from typing import Iterable

from google.cloud.storage.blob import Blob

from source_gcs.helpers import GCSUploadableRemoteFile


logger = logging.getLogger("airbyte")


class ZipHelper:
    BUFFER_SIZE_DEFAULT = 1024 * 1024

    def __init__(self, blob: Blob, zip_file: GCSUploadableRemoteFile, tmp_dir_path: str):
        self._blob = blob
        self._size = blob.size
        self._zip_file = zip_file
        self._tmp_dir_path = tmp_dir_path

    def _chunk_download(self) -> bytes:
        start = 0
        end = self.BUFFER_SIZE_DEFAULT
        object_bytes = b""
        while start < self._size:
            object_bytes_chunk = self._blob.download_as_bytes(start=start, end=end)
            object_bytes += object_bytes_chunk
            start = end + 1
            end = start + self.BUFFER_SIZE_DEFAULT
            if end > self._size:
                end = self._size

        return object_bytes

    def _extract_files_to_tmp_directory(self, object_bytes: bytes, tmp_dir_path: str) -> None:
        with io.BytesIO(object_bytes) as bytes_io:
            with zipfile.ZipFile(bytes_io, "r") as zf:
                zf.extractall(tmp_dir_path)

    def get_gcs_remote_files(self) -> Iterable[GCSUploadableRemoteFile]:
        extract_dir = tempfile.mkdtemp(dir=self._tmp_dir_path)
        self._extract_files_to_tmp_directory(self._chunk_download(), extract_dir)

        for dirpath, _, filenames in os.walk(extract_dir):
            for unzipped_file in filenames:
                file_path = os.path.join(dirpath, unzipped_file)
                logger.info(f"Picking up file {unzipped_file} from zip archive {self._blob.public_url}.")
                file_extension = unzipped_file.split(".")[-1]

                yield GCSUploadableRemoteFile(
                    uri=file_path,
                    last_modified=self._zip_file.last_modified,
                    mime_type=file_extension,
                    displayed_uri=self._zip_file.uri,  # uri to remote file .zip
                    blob=self._blob,
                )
