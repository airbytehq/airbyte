#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
import io
import json
import tempfile
from datetime import datetime
from io import IOBase
from typing import Any, Iterable, List, Mapping, Optional

import avro.io as ai
import avro.schema as avro_schema
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.file_based.availability_strategy import AbstractFileBasedAvailabilityStrategy, DefaultFileBasedAvailabilityStrategy
from airbyte_cdk.sources.file_based.config.abstract_file_based_spec import AbstractFileBasedSpec
from airbyte_cdk.sources.file_based.discovery_policy import AbstractDiscoveryPolicy, DefaultDiscoveryPolicy
from airbyte_cdk.sources.file_based.file_based_source import DEFAULT_MAX_HISTORY_SIZE, FileBasedSource
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_validation_policies import DEFAULT_SCHEMA_VALIDATION_POLICIES, AbstractSchemaValidationPolicy
from avro import datafile
from pydantic import AnyUrl, Field


class InMemoryFilesSource(FileBasedSource):
    def __init__(
        self,
        files: Mapping[str, Any],
        file_type: str,
        availability_strategy: Optional[AbstractFileBasedAvailabilityStrategy],
        discovery_policy: Optional[AbstractDiscoveryPolicy],
        validation_policies: Mapping[str, AbstractSchemaValidationPolicy],
        parsers: Mapping[str, FileTypeParser],
        stream_reader: Optional[AbstractFileBasedStreamReader],
        catalog: Optional[Mapping[str, Any]],
        file_write_options: Mapping[str, Any],
        max_history_size: int,
    ):
        stream_reader = stream_reader or InMemoryFilesStreamReader(files=files, file_type=file_type, file_write_options=file_write_options)
        availability_strategy = availability_strategy or DefaultFileBasedAvailabilityStrategy(stream_reader)  # type: ignore[assignment]
        super().__init__(
            stream_reader,
            catalog=ConfiguredAirbyteCatalog(streams=catalog["streams"]) if catalog else None,
            availability_strategy=availability_strategy,
            spec_class=InMemorySpec,
            discovery_policy=discovery_policy or DefaultDiscoveryPolicy(),
            parsers=parsers,
            validation_policies=validation_policies or DEFAULT_SCHEMA_VALIDATION_POLICIES,
            max_history_size=max_history_size or DEFAULT_MAX_HISTORY_SIZE,
        )

        # Attributes required for test purposes
        self.files = files
        self.file_type = file_type


class InMemoryFilesStreamReader(AbstractFileBasedStreamReader):
    files: Mapping[str, Mapping[str, Any]]
    file_type: str
    file_write_options: Optional[Mapping[str, Any]]

    def get_matching_files(
        self,
        globs: List[str],
    ) -> Iterable[RemoteFile]:
        yield from AbstractFileBasedStreamReader.filter_files_by_globs(
            [
                RemoteFile(uri=f, last_modified=datetime.strptime(data["last_modified"], "%Y-%m-%dT%H:%M:%S.%fZ"), file_type=self.file_type)
                for f, data in self.files.items()
            ],
            globs,
        )

    def open_file(self, file: RemoteFile) -> IOBase:
        if file.file_type == "csv":
            return self._make_csv_file_contents(file.uri)
        elif file.file_type == "jsonl":
            return self._make_jsonl_file_contents(file.uri)
        else:
            raise NotImplementedError(f"No implementation for file type: {file.file_type}")

    def _make_csv_file_contents(self, file_name: str) -> IOBase:
        fh = io.StringIO()
        if self.file_write_options:
            csv.register_dialect("in_memory_dialect", **self.file_write_options)
            writer = csv.writer(fh, dialect="in_memory_dialect")
            writer.writerows(self.files[file_name]["contents"])
            csv.unregister_dialect("in_memory_dialect")
        else:
            writer = csv.writer(fh)
            writer.writerows(self.files[file_name]["contents"])
        fh.seek(0)
        return fh

    def _make_jsonl_file_contents(self, file_name: str) -> IOBase:
        fh = io.BytesIO()

        for line in self.files[file_name]["contents"]:
            try:
                fh.write((json.dumps(line) + "\n").encode("utf-8"))
            except TypeError:
                # Intentionally trigger json validation error
                fh.write((str(line) + "\n").encode("utf-8"))
        fh.seek(0)
        return fh


class InMemorySpec(AbstractFileBasedSpec):
    @classmethod
    def documentation_url(cls) -> AnyUrl:
        return AnyUrl(scheme="https", url="https://docs.airbyte.com/integrations/sources/in_memory_files")  # type: ignore

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
        return io.BytesIO(self._create_file(file.uri))

    def _create_file(self, file_name: str) -> bytes:
        contents = self.files[file_name]["contents"]
        schema = self.files[file_name].get("schema")

        df = pd.DataFrame(contents[1:], columns=contents[0])
        with tempfile.TemporaryFile() as fp:
            table = pa.Table.from_pandas(df, schema)
            pq.write_table(table, fp)

            fp.seek(0)
            return fp.read()


class TemporaryAvroFilesStreamReader(InMemoryFilesStreamReader):
    """
    A file reader that writes RemoteFiles to a temporary file and then reads them back.
    """

    def open_file(self, file: RemoteFile) -> IOBase:
        return io.BytesIO(self._make_file_contents(file.uri))

    def _make_file_contents(self, file_name: str) -> bytes:
        contents = self.files[file_name]["contents"]
        schema = self.files[file_name]["schema"]
        stream_schema = avro_schema.make_avsc_object(schema)

        rec_writer = ai.DatumWriter(stream_schema)
        with tempfile.TemporaryFile() as fp:
            file_writer = datafile.DataFileWriter(fp, rec_writer, stream_schema)
            for content in contents:
                data = {col["name"]: content[i] for i, col in enumerate(schema["fields"])}
                file_writer.append(data)
            file_writer.flush()
            fp.seek(0)
            return fp.read()
