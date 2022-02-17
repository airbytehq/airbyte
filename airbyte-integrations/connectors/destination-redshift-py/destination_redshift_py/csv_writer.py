import csv
import gzip
import shutil
import tempfile
from pathlib import Path
from typing import Union, List, Optional

from dotmap import DotMap

from destination_redshift_py.table import Table

CSV_EXTENSION = "csv"
GZIP_EXTENSION = "gzip"


class CSVWriter:
    def __init__(self, table: Table):
        self.table = table

        self._temporary_file = None
        self._dict_writer = None

        self._rows = 0

    def initialize_writer(self):
        self._temporary_file = tempfile.NamedTemporaryFile(delete=True, suffix=f".{CSV_EXTENSION}")

        self._dict_writer = csv.DictWriter(open(self._temporary_file.name, "w"), fieldnames=self.table.field_names)
        self._dict_writer.writeheader()

        self._rows = 0

    def write(self, records: Union[DotMap, List[DotMap]]):
        if not isinstance(records, list):
            records = [records]

        self._dict_writer.writerows(records)
        self._rows += len(records)

    def flush_gzipped(self) -> Optional[gzip.GzipFile]:
        if self._rows:
            temporary_gzip_file = gzip.open(f"{self._temporary_file.name}.{GZIP_EXTENSION}", "wb")

            temp_file = self._temporary_file
            self.initialize_writer()

            with temporary_gzip_file as f_out:
                shutil.copyfileobj(temp_file, f_out)

            return temporary_gzip_file

    def delete_gzip_file(self, gzip_file: gzip.GzipFile):
        Path(gzip_file.name).unlink()
