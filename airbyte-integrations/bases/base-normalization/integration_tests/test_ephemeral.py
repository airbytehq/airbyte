#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import os
import pathlib
import re
import shutil
import tempfile
from distutils.dir_util import copy_tree
from typing import Any, Dict

import pytest
from integration_tests.dbt_integration_test import DbtIntegrationTest
from normalization.destination_type import DestinationType
from normalization.transform_catalog import TransformCatalog

temporary_folders = set()
dbt_test_utils = DbtIntegrationTest()


@pytest.fixture(scope="module", autouse=True)
def before_all_tests(request):
    destinations_to_test = dbt_test_utils.get_test_targets()
    # set clean-up args to clean target destination after the test
    clean_up_args = {
        "destination_type": [d for d in DestinationType if d.value in destinations_to_test],
        "test_type": "ephemeral",
        "tmp_folders": temporary_folders,
    }
    if DestinationType.POSTGRES.value not in destinations_to_test:
        destinations_to_test.append(DestinationType.POSTGRES.value)
    dbt_test_utils.set_target_schema("test_ephemeral")
    dbt_test_utils.change_current_test_dir(request)
    dbt_test_utils.setup_db(destinations_to_test)
    os.environ["PATH"] = os.path.abspath("../.venv/bin/") + ":" + os.environ["PATH"]
    yield
    dbt_test_utils.clean_tmp_tables(**clean_up_args)
    dbt_test_utils.tear_down_db()
    for folder in temporary_folders:
        print(f"Deleting temporary test folder {folder}")
        shutil.rmtree(folder, ignore_errors=True)


@pytest.fixture
def setup_test_path(request):
    dbt_test_utils.change_current_test_dir(request)
    print(f"Running from: {pathlib.Path().absolute()}")
    print(f"Current PATH is: {os.environ['PATH']}")
    yield
    os.chdir(request.config.invocation_dir)


@pytest.mark.parametrize("column_count", [1000])
@pytest.mark.parametrize("destination_type", list(DestinationType))
def test_destination_supported_limits(destination_type: DestinationType, column_count: int):
    if destination_type.value not in dbt_test_utils.get_test_targets() or destination_type.value == DestinationType.MYSQL.value:
        # In MySQL, the max number of columns is limited by row size (8KB),
        # not by absolute column count. It is way fewer than 1000.
        pytest.skip(f"Destinations {destination_type} is not in NORMALIZATION_TEST_TARGET env variable (MYSQL is also skipped)")
    if destination_type.value == DestinationType.ORACLE.value:
        # Airbyte uses a few columns for metadata and Oracle limits are right at 1000
        column_count = 993
    if destination_type.value == DestinationType.MSSQL.value:
        column_count = 999
    run_test(destination_type, column_count)


@pytest.mark.parametrize(
    "integration_type, column_count, expected_exception_message",
    [
        ("Postgres", 1665, "target lists can have at most 1664 entries"),
        ("BigQuery", 3000, "The view is too large."),
        ("Snowflake", 2000, "Operation failed because soft limit on objects of type 'Column' per table was exceeded."),
        ("Redshift", 1665, "target lists can have at most 1664 entries"),
        ("MySQL", 250, "Row size too large"),
        ("Oracle", 1001, "ORA-01792: maximum number of columns in a table or view is 1000"),
        ("MSSQL", 1025, "exceeds the maximum of 1024 columns."),
    ],
)
def test_destination_failure_over_limits(integration_type: str, column_count: int, expected_exception_message: str, setup_test_path):
    destination_type = DestinationType.from_string(integration_type)
    if destination_type.value not in dbt_test_utils.get_test_targets():
        pytest.skip(f"Destinations {destination_type} is not in NORMALIZATION_TEST_TARGET env variable")
    run_test(destination_type, column_count, expected_exception_message)


def test_empty_streams(setup_test_path):
    run_test(DestinationType.POSTGRES, 0)


def test_stream_with_1_airbyte_column(setup_test_path):
    run_test(DestinationType.POSTGRES, 1)


def run_test(destination_type: DestinationType, column_count: int, expected_exception_message: str = ""):
    if destination_type.value == DestinationType.ORACLE.value:
        # Oracle does not allow changing to random schema
        dbt_test_utils.set_target_schema("test_normalization")
    elif destination_type.value == DestinationType.REDSHIFT.value:
        # set unique schema for Redshift test
        dbt_test_utils.set_target_schema(dbt_test_utils.generate_random_string("test_ephemeral_"))
    else:
        dbt_test_utils.set_target_schema("test_ephemeral")
    print("Testing ephemeral")
    integration_type = destination_type.value
    # Create the test folder with dbt project and appropriate destination settings to run integration tests from
    test_root_dir = setup_test_dir(integration_type)
    destination_config = dbt_test_utils.generate_profile_yaml_file(destination_type, test_root_dir)
    # generate a catalog and associated dbt models files
    generate_dbt_models(destination_type, test_root_dir, column_count)
    # Use destination connector to create empty _airbyte_raw_* tables to use as input for the test
    assert setup_input_raw_data(integration_type, test_root_dir, destination_config)
    dbt_test_utils.dbt_check(destination_type, test_root_dir)
    if expected_exception_message:
        with pytest.raises(AssertionError):
            dbt_test_utils.dbt_run(destination_type, test_root_dir)
        assert search_logs_for_pattern(test_root_dir + "/dbt_output.log", expected_exception_message)
    else:
        dbt_test_utils.dbt_run(destination_type, test_root_dir)


def search_logs_for_pattern(log_file: str, pattern: str):
    with open(log_file, "r") as file:
        for line in file:
            if re.search(pattern, line):
                return True
    return False


def setup_test_dir(integration_type: str) -> str:
    """
    We prepare a clean folder to run the tests from.
    """
    test_root_dir = f"{pathlib.Path().joinpath('..', 'build', 'normalization_test_output', integration_type.lower()).resolve()}"
    os.makedirs(test_root_dir, exist_ok=True)
    test_root_dir = tempfile.mkdtemp(dir=test_root_dir)
    temporary_folders.add(test_root_dir)
    shutil.rmtree(test_root_dir, ignore_errors=True)
    print(f"Setting up test folder {test_root_dir}")
    copy_tree("../dbt-project-template", test_root_dir)
    if integration_type == DestinationType.MSSQL.value:
        copy_tree("../dbt-project-template-mssql", test_root_dir)
    elif integration_type == DestinationType.MYSQL.value:
        copy_tree("../dbt-project-template-mysql", test_root_dir)
    elif integration_type == DestinationType.ORACLE.value:
        copy_tree("../dbt-project-template-oracle", test_root_dir)
    elif integration_type == DestinationType.SNOWFLAKE.value:
        copy_tree("../dbt-project-template-snowflake", test_root_dir)
    return test_root_dir


def setup_input_raw_data(integration_type: str, test_root_dir: str, destination_config: Dict[str, Any]) -> bool:
    """
    This should populate the associated "raw" tables from which normalization is reading from when running dbt CLI.
    """
    config_file = os.path.join(test_root_dir, "destination_config.json")
    with open(config_file, "w") as f:
        f.write(json.dumps(destination_config))
    commands = [
        "docker",
        "run",
        "--rm",
        "--init",
        "-v",
        f"{test_root_dir}:/data",
        "--network",
        "host",
        "-i",
        f"airbyte/destination-{integration_type.lower()}:dev",
        "write",
        "--config",
        "/data/destination_config.json",
        "--catalog",
        "/data/catalog.json",
    ]
    # Force a reset in destination raw tables
    return dbt_test_utils.run_destination_process("", test_root_dir, commands)


def generate_dbt_models(destination_type: DestinationType, test_root_dir: str, column_count: int):
    """
    This is the normalization step generating dbt models files from the destination_catalog.json taken as input.
    """
    output_directory = os.path.join(test_root_dir, "models", "generated")
    shutil.rmtree(output_directory, ignore_errors=True)
    catalog_config = {
        "streams": [
            {
                "stream": {
                    "name": dbt_test_utils.generate_random_string(f"stream_with_{column_count}_columns"),
                    "json_schema": {
                        "type": ["null", "object"],
                        "properties": {},
                    },
                    "supported_sync_modes": ["incremental"],
                    "source_defined_cursor": True,
                    "default_cursor_field": [],
                },
                "sync_mode": "incremental",
                "cursor_field": [],
                "destination_sync_mode": "overwrite",
            }
        ]
    }
    if column_count == 1:
        catalog_config["streams"][0]["stream"]["json_schema"]["properties"]["_airbyte_id"] = {"type": "integer"}
    else:
        for column in [dbt_test_utils.random_string(5) for _ in range(column_count)]:
            catalog_config["streams"][0]["stream"]["json_schema"]["properties"][column] = {"type": "string"}
    catalog = os.path.join(test_root_dir, "catalog.json")
    with open(catalog, "w") as fh:
        fh.write(json.dumps(catalog_config))

    transform_catalog = TransformCatalog()
    transform_catalog.config = {
        "integration_type": destination_type.value,
        "schema": dbt_test_utils.target_schema,
        "catalog": [catalog],
        "output_path": output_directory,
        "json_column": "_airbyte_data",
        "profile_config_dir": test_root_dir,
    }
    transform_catalog.process_catalog()
