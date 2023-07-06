#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
import io
from datetime import datetime
from io import IOBase
from typing import Any, Dict, Iterable, List, Optional
import tempfile

from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


class TemporaryFilesStreamReader(AbstractFileBasedStreamReader):
    #FIXME: this is tightly coupled with parquet files.
    # Either rename or decouple
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
        return io.BytesIO(self._make_file_contents(file.uri))

    def _make_file_contents(self, file_name: str):
        contents = self.files[file_name]["contents"]
        schema = self.files[file_name].get("schema")

        df = pd.DataFrame(contents[1:], columns=contents[0])
        with tempfile.TemporaryFile() as fp:
            table = pa.Table.from_pandas(df, schema)
            pq.write_table(table, fp)

            fp.seek(0)
            return fp.read()

if __name__ == "__main__":

    with tempfile.TemporaryFile() as fp:
        df = pd.DataFrame({'col1': [1, 2], 'col2': ["hello", "world"]})
        table = pa.Table.from_pandas(df)
        pq.write_table(table, fp)
        table_read = pq.read_table(fp)

        files = {
            "a.parquet": {
                "contents": [
                    ("col1", "col2"),
                    ("val11", "val12"),
                    ("val21", "val22"),
                ],
                "last_modified": "2023-06-05T03:54:07.000Z",
            }
        }
        file_type = "parquet"
        stream_reader = TemporaryFilesStreamReader(files=files, file_type=file_type)

        remote_file = RemoteFile(uri="a.parquet", last_modified=datetime.strptime("2023-06-05T03:54:07.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"), file_type=file_type)
        file_pointer = stream_reader.open_file(remote_file)
        output = pq.read_table(file_pointer)
        for row in output:
            print(row)

