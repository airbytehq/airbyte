from .avro_parser import AvroParser
from .csv_parser import CsvParser
from .jsonl_parser import JsonlParser
from .parquet_parser import ParquetParser

default_parsers = {
    "avro": AvroParser(),
    "csv": CsvParser(),
    "jsonl": JsonlParser(),
    "parquet": ParquetParser(),
}

__all__ = ["AvroParser", "CsvParser", "JsonlParser", "ParquetParser", "default_parsers"]
