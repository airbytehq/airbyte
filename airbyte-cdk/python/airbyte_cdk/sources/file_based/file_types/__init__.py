from typing import Mapping

from .avro_parser import AvroParser
from .csv_parser import CsvParser
from .file_type_parser import FileTypeParser
from .jsonl_parser import JsonlParser
from .parquet_parser import ParquetParser

default_parsers: Mapping[str, FileTypeParser] = {
    "avro": AvroParser(),
    "csv": CsvParser(),
    "jsonl": JsonlParser(),
    "parquet": ParquetParser(),
}

__all__ = ["AvroParser", "CsvParser", "JsonlParser", "ParquetParser", "default_parsers"]
