#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import io
import tempfile
from datetime import datetime
from io import IOBase
from typing import Any, Dict, Iterable, List, Optional
from memory_profiler import profile

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.remote_file import RemoteFile


class TemporaryParquetFilesStreamReader(AbstractFileBasedStreamReader):
    """
    A file reader that writes RemoteFiles to a temporary file and then reads them back.
    """

    files: Dict[str, dict[str, Any]]
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
