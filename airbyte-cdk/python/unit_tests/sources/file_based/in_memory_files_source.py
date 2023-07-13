#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
import io
import tempfile
from datetime import datetime
from io import IOBase
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.file_based.config.abstract_file_based_spec import AbstractFileBasedSpec
from airbyte_cdk.sources.file_based.default_file_based_availability_strategy import DefaultFileBasedAvailabilityStrategy
from airbyte_cdk.sources.file_based.discovery_policy import AbstractDiscoveryPolicy
from airbyte_cdk.sources.file_based.file_based_source import DEFAULT_MAX_HISTORY_SIZE, FileBasedSource
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_validation_policies import DEFAULT_SCHEMA_VALIDATION_POLICIES, AbstractSchemaValidationPolicy
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from pydantic import AnyUrl, Field


class InMemoryFilesSource(FileBasedSource):
    def __init__(
            self,
            files,
            file_type,
            availability_strategy: AvailabilityStrategy,
            discovery_policy: AbstractDiscoveryPolicy,
            validation_policies: Dict[str, AbstractSchemaValidationPolicy],
            parsers: Dict[str, FileTypeParser],
            stream_reader: AbstractFileBasedStreamReader,
            catalog: Optional[Dict[str, Any]],
            file_write_options: Dict[str, Any],
            max_history_size: int,
    ):
        stream_reader = stream_reader or InMemoryFilesStreamReader(files=files, file_type=file_type, file_write_options=file_write_options)
        availability_strategy = availability_strategy or DefaultFileBasedAvailabilityStrategy(stream_reader)
        super().__init__(
            stream_reader,
            catalog=ConfiguredAirbyteCatalog(streams=catalog["streams"]) if catalog else None,
            availability_strategy=availability_strategy,
            spec_class=InMemorySpec,
            discovery_policy=discovery_policy,
            parsers=parsers,
            validation_policies=validation_policies or DEFAULT_SCHEMA_VALIDATION_POLICIES,
            max_history_size=max_history_size or DEFAULT_MAX_HISTORY_SIZE
        )

        # Attributes required for test purposes
        self.files = files
        self.file_type = file_type


class InMemoryFilesStreamReader(AbstractFileBasedStreamReader):
    files: Dict[str, dict]
    file_type: str
    file_write_options: Optional[Dict[str, Any]]

    def get_matching_files(
            self,
            globs: List[str],
    ) -> Iterable[RemoteFile]:
        yield from AbstractFileBasedStreamReader.filter_files_by_globs([
            RemoteFile(uri=f, last_modified=datetime.strptime(data["last_modified"], "%Y-%m-%dT%H:%M:%S.%fZ"), file_type=self.file_type)
            for f, data in self.files.items()
        ], globs)

    def open_file(self, file: RemoteFile) -> IOBase:
        return io.StringIO(self._make_file_contents(file.uri))

    def _make_file_contents(self, file_name: str):
        if self.file_type == "csv":
            return self._make_csv_file_contents(file_name)
        else:
            raise NotImplementedError(f"No implementation for filename: {file_name}")

    def _make_csv_file_contents(self, file_name: str) -> str:
        fh = io.StringIO()
        if self.file_write_options:
            csv.register_dialect("in_memory_dialect", **self.file_write_options)
            writer = csv.writer(fh, dialect="in_memory_dialect")
            writer.writerows(self.files[file_name]["contents"])
            csv.unregister_dialect("in_memory_dialect")
        else:
            writer = csv.writer(fh)
            writer.writerows(self.files[file_name]["contents"])
        return fh.getvalue()


class InMemorySpec(AbstractFileBasedSpec):
    @classmethod
    def documentation_url(cls) -> AnyUrl:
        return AnyUrl(scheme="https", url="https://docs.airbyte.com/integrations/sources/in_memory_files")

    start_date: Optional[str] = Field(
        title="Start Date",
        description="UTC date and time in the format 2017-01-25T00:00:00Z. Any file modified before this date will not be replicated.",
        examples=["2021-01-01T00:00:00Z"],
        format="date-time",
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
        order=1,
    )


class TemporaryParquetFilesStreamReader(InMemoryFilesStreamReader):
    """
    A file reader that writes RemoteFiles to a temporary file and then reads them back.
    """

    def open_file(self, file: RemoteFile) -> IOBase:
        return io.BytesIO(self._make_file_contents(file.uri))

    def _make_file_contents(self, file_name: str) -> bytes:
        contents = self.files[file_name]["contents"]
        schema = self.files[file_name].get("schema")

        df = pd.DataFrame(contents[1:], columns=contents[0])
        with tempfile.TemporaryFile() as fp:
            table = pa.Table.from_pandas(df, schema)
            pq.write_table(table, fp)

            fp.seek(0)
            return fp.read()
