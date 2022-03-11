#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json

from source_s3 import SourceS3
import pytest
from airbyte_cdk.logger import AirbyteLogger

LOGGER = AirbyteLogger()


def test_transform_backslash_t_to_tab(tmp_path):
    config_file = tmp_path / "config.json"
    with open(config_file, "w") as fp:
        json.dump({"format": {"delimiter": "\\t"}}, fp)
    source = SourceS3()
    config = source.read_config(config_file)
    assert config["format"]["delimiter"] == "\t"


@pytest.mark.parametrize(
    "config, fails",
    [
        ({"dataset": "test1,test1"}, True),
        ({"dataset": "test1,test2", "path_pattern": '{"test3":"**"}'}, True),
        ({"dataset": "test1,test2", "schema": '{"test3":null}'}, True),
        ({"dataset": "test1,test2", "schema": '{"test3":null}'}, True),
        (
            {
                "dataset": "test1,test2",
                "format": {"filetype": "csv", "advanced_options": '{"test3":null}'},
            },
            True,
        ),
        (
            {
                "dataset": "test1,test2",
                "format": {"filetype": "parquet", "columns": '{"test3":null}'},
            },
            True,
        ),
        (
            {
                "dataset": "test1,test2",
                "path_pattern": '{"test1":"test1.csv"}',
                "schema": '{"test2":null}',
                "format": {"filetype": "csv", "advanced_options": '{"test2":null}'},
            },
            False,
        ),
        (
            {
                "dataset": "test1,test2",
                "path_pattern": '{"test1":"test1.csv"}',
                "schema": '{"test2":null}',
                "format": {"filetype": "parquet", "columns": '{"test2":null}'},
            },
            False,
        ),
    ],
)
def test_source_check_config(config, fails):
    source = SourceS3()
    if not fails:
        source.check_config(config)
    else:
        with pytest.raises(Exception) as e_info:
            LOGGER.info("Testing EXPECTED FAILURE check_config()")
            source.check_config(config)
        assert "check_config" in str(e_info.value)
        LOGGER.info(f"Failed as expected, error: {e_info}")


@pytest.mark.parametrize(
    "config, expected_split_configs",
    [
        (
            # single stream parqet format
            {
                "dataset": "test",
                "path_pattern": '{"test":"test.csv"}',
                "schema": '{"test": {"column_1": "object"}}',
                "format": {
                    "filetype": "parquet",
                    "columns": '{"test":["col_1","col_2"]}',
                },
            },
            {
                "test": {
                    "dataset": "test",
                    "path_pattern": "test.csv",
                    "schema": json.dumps({"column_1": "object"}),
                    "format": {"filetype": "parquet", "columns": ["col_1", "col_2"]},
                },
            },
        ),
        (
            # single sream csv format
            {
                "dataset": "test",
                "path_pattern": '{"test":"test.csv"}',
                "schema": '{"test": {"column_1": "object"}}',
                "format": {
                    "filetype": "csv",
                    "advanced_options": '{"test":{"column_names": ["column1", "column2"]}}',
                },
            },
            {
                "test": {
                    "dataset": "test",
                    "path_pattern": "test.csv",
                    "schema": json.dumps({"column_1": "object"}),
                    "format": {
                        "filetype": "csv",
                        "advanced_options": json.dumps(
                            {"column_names": ["column1", "column2"]}
                        ),
                    },
                },
            },
        ),
        (
            # two streams parquet format
            {
                "dataset": "test1,test2",
                "path_pattern": '{"test1":"test1.csv"}',
                "schema": '{"test2": {"column_1": "object"}}',
                "format": {
                    "filetype": "parquet",
                    "columns": '{"test2":["col_1","col_2"]}',
                },
            },
            {
                "test1": {
                    "dataset": "test1",
                    "path_pattern": "test1.csv",
                    "schema": None,
                    "format": {"filetype": "parquet", "columns": None},
                },
                "test2": {
                    "dataset": "test2",
                    "path_pattern": "**",
                    "schema": json.dumps({"column_1": "object"}),
                    "format": {"filetype": "parquet", "columns": ["col_1", "col_2"]},
                },
            },
        ),
        (
            # two streams csv format
            {
                "dataset": "test1,test2",
                "path_pattern": '{"test1":"test1.csv"}',
                "schema": '{"test1": {"column_1": "object"}}',
                "format": {
                    "filetype": "csv",
                    "advanced_options": '{"test2":{"column_names": ["column1", "column2"]}}',
                },
            },
            {
                "test1": {
                    "dataset": "test1",
                    "path_pattern": "test1.csv",
                    "schema": json.dumps({"column_1": "object"}),
                    "format": {"filetype": "csv", "advanced_options": "{}"},
                },
                "test2": {
                    "dataset": "test2",
                    "path_pattern": "**",
                    "schema": None,
                    "format": {
                        "filetype": "csv",
                        "advanced_options": json.dumps(
                            {"column_names": ["column1", "column2"]}
                        ),
                    },
                },
            },
        ),
    ],
)
def test_source_split_config_by_stream(config, expected_split_configs):
    source = SourceS3()
    assert source.split_config_by_stream(config) == expected_split_configs
