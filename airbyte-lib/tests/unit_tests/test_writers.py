# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from pathlib import Path
import pytest
from airbyte_lib._file_writers.base import FileWriterBase, FileWriterBatchHandle, FileWriterConfigBase
from airbyte_lib._file_writers.parquet import ParquetWriter, ParquetWriterConfig
from numpy import source


def test_parquet_writer_config_initialization():
    config = ParquetWriterConfig(cache_dir='test_path')
    assert config.cache_dir == Path('test_path')

def test_parquet_writer_config_inheritance():
    assert issubclass(ParquetWriterConfig, FileWriterConfigBase)

def test_parquet_writer_initialization():
    config = ParquetWriterConfig(cache_dir='test_path')
    writer = ParquetWriter(config)
    assert writer.config == config

def test_parquet_writer_inheritance():
    assert issubclass(ParquetWriter, FileWriterBase)

def test_parquet_writer_has_config():
    config = ParquetWriterConfig(cache_dir='test_path')
    writer = ParquetWriter(config)
    assert hasattr(writer, 'config')

def test_parquet_writer_has_source_catalog():
    config = ParquetWriterConfig(cache_dir='test_path')
    writer = ParquetWriter(config)

def test_parquet_writer_source_catalog_is_none():
    config = ParquetWriterConfig(cache_dir='test_path')
    writer = ParquetWriter(config)
