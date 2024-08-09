from typing import Any, Mapping, Type

from airbyte_cdk.sources.file_based.config.avro_format import AvroFormat
from airbyte_cdk.sources.file_based.config.excel_format import ExcelFormat
from airbyte_cdk.sources.file_based.config.csv_format import CsvFormat
from airbyte_cdk.sources.file_based.config.jsonl_format import JsonlFormat
from airbyte_cdk.sources.file_based.config.parquet_format import ParquetFormat
from airbyte_cdk.sources.file_based.config.unstructured_format import UnstructuredFormat

from .avro_parser import AvroParser
from .csv_parser import CsvParser
from .excel_parser import ExcelParser
from .file_type_parser import FileTypeParser
from .jsonl_parser import JsonlParser
from .parquet_parser import ParquetParser
from .unstructured_parser import UnstructuredParser

default_parsers: Mapping[Type[Any], FileTypeParser] = {
    AvroFormat: AvroParser(),
    CsvFormat: CsvParser(),
    ExcelFormat: ExcelParser(),
    JsonlFormat: JsonlParser(),
    ParquetFormat: ParquetParser(),
    UnstructuredFormat: UnstructuredParser(),
}

__all__ = ["AvroParser", "CsvParser", "ExcelParser", "JsonlParser", "ParquetParser", "UnstructuredParser", "default_parsers"]
