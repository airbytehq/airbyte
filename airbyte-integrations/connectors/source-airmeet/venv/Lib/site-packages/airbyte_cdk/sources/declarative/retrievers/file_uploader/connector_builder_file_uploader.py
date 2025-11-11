#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass

from airbyte_cdk.sources.declarative.types import Record

from .default_file_uploader import DefaultFileUploader
from .file_uploader import FileUploader


@dataclass
class ConnectorBuilderFileUploader(FileUploader):
    """
    Connector builder file uploader
    Acts as a decorator or wrapper around a FileUploader instance, copying the attributes from record.file_reference into the record.data.
    """

    file_uploader: DefaultFileUploader

    def upload(self, record: Record) -> None:
        self.file_uploader.upload(record=record)
        record.data["source_file_relative_path"] = record.file_reference.source_file_relative_path  # type: ignore
