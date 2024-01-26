# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest

from airbyte_lib._file_writers import ParquetWriterConfig
from airbyte_lib.caches.base import SQLCacheBase, SQLCacheConfigBase
from airbyte_lib.caches.duckdb import DuckDBCacheBase, DuckDBCacheConfig


def test_duck_db_cache_config_initialization():
    config = DuckDBCacheConfig(db_path='test_path', schema_name='test_schema')
    assert config.db_path == Path('test_path')
    assert config.schema_name == 'test_schema'

def test_duck_db_cache_config_default_schema_name():
    config = DuckDBCacheConfig(db_path='test_path')
    assert config.schema_name == 'main'

def test_get_sql_alchemy_url():
    config = DuckDBCacheConfig(db_path='test_path', schema_name='test_schema')
    assert config.get_sql_alchemy_url() == 'duckdb:///test_path'

def test_get_sql_alchemy_url_with_default_schema_name():
    config = DuckDBCacheConfig(db_path='test_path')
    assert config.get_sql_alchemy_url() == 'duckdb:///test_path'

def test_duck_db_cache_config_inheritance():
    assert issubclass(DuckDBCacheConfig, SQLCacheConfigBase)
    assert issubclass(DuckDBCacheConfig, ParquetWriterConfig)

def test_duck_db_cache_config_get_sql_alchemy_url():
    config = DuckDBCacheConfig(db_path='test_path', schema_name='test_schema')
    assert config.get_sql_alchemy_url() == 'duckdb:///test_path'

def test_duck_db_cache_config_get_database_name():
    config = DuckDBCacheConfig(db_path='test_path/test_db.duckdb', schema_name='test_schema')
    assert config.get_database_name() == 'test_db'

def test_duck_db_cache_base_inheritance():
    assert issubclass(DuckDBCacheBase, SQLCacheBase)

def test_duck_db_cache_config_default_schema_name():
    config = DuckDBCacheConfig(db_path='test_path')
    assert config.schema_name == 'main'

def test_duck_db_cache_config_get_sql_alchemy_url_with_default_schema_name():
    config = DuckDBCacheConfig(db_path='test_path')
    assert config.get_sql_alchemy_url() == 'duckdb:///test_path'

def test_duck_db_cache_config_get_database_name_with_default_schema_name():
    config = DuckDBCacheConfig(db_path='test_path/test_db.duckdb')
    assert config.get_database_name() == 'test_db'

def test_duck_db_cache_config_inheritance_from_sql_cache_config_base():
    assert issubclass(DuckDBCacheConfig, SQLCacheConfigBase)

def test_duck_db_cache_config_inheritance_from_parquet_writer_config():
    assert issubclass(DuckDBCacheConfig, ParquetWriterConfig)
