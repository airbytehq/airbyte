#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import json
import os
import pathlib
import shutil
import tempfile
from typing import Any, Dict

import pytest
from integration_tests.integration_test_utils import (
    change_current_test_dir,
    copy_replace,
    dbt_run,
    generate_profile_yaml_file,
    random_string,
    run_destination_process,
    setup_postgres_db,
    target_schema,
    tear_down_postgres_db,
)
from normalization.destination_type import DestinationType
from normalization.transform_catalog.catalog_processor import CatalogProcessor

temporary_folders = set()


@pytest.fixture(scope="module", autouse=True)
def before_all_tests(request):
    change_current_test_dir(request)
    setup_postgres_db()
    os.environ["PATH"] = os.path.abspath("../.venv/bin/") + ":" + os.environ["PATH"]
    yield
    tear_down_postgres_db()
    for folder in temporary_folders:
        print(f"Deleting temporary test folder {folder}")
        shutil.rmtree(folder, ignore_errors=True)


@pytest.fixture
def setup_test_path(request):
    change_current_test_dir(request)
    print(f"Running from: {pathlib.Path().absolute()}")
    print(f"Current PATH is: {os.environ['PATH']}")
    yield
    os.chdir(request.config.invocation_dir)


@pytest.mark.parametrize("column_count", [480, 490, 1000])
@pytest.mark.parametrize(
    "integration_type",
    [
        "Postgres",
    ],
)
# Databases are ran in local containers, we can test more parameters as it's faster
def test_databases(integration_type: str, column_count: int, setup_test_path):
    run_test(integration_type, column_count)


@pytest.mark.parametrize("column_count", [1000])
@pytest.mark.parametrize(
    "integration_type",
    [
        "BigQuery",
        "Snowflake",
        "Redshift",
    ],
)
def test_warehouses(integration_type: str, column_count: int, setup_test_path):
    run_test(integration_type, column_count)


def test_empty_streams(setup_test_path):
    with pytest.raises(EOFError):
        run_test("postgres", 0)


def test_stream_with_1_airbyte_column(setup_test_path):
    run_test("postgres", 1)


def run_test(integration_type: str, column_count: int):
    print("Testing ephemeral")
    destination_type = DestinationType.from_string(integration_type)
    # Create the test folder with dbt project and appropriate destination settings to run integration tests from
    test_root_dir = setup_test_dir(integration_type, "test_ephemeral")
    destination_config = generate_profile_yaml_file(destination_type, test_root_dir)
    # generate a catalog and associated dbt models files
    generate_dbt_models(destination_type, test_root_dir, column_count)
    # Use destination connector to create empty _airbyte_raw_* tables to use as input for the test
    assert setup_input_raw_data(integration_type, test_root_dir, destination_config)
    dbt_run(test_root_dir)


def setup_test_dir(integration_type: str, test_resource_name: str) -> str:
    """
    We prepare a clean folder to run the tests from.
    """
    test_root_dir = tempfile.mkdtemp(dir="/tmp/", prefix="normalization_test_", suffix=f"_{integration_type.lower()}")
    temporary_folders.add(test_root_dir)
    shutil.rmtree(test_root_dir, ignore_errors=True)
    os.makedirs(test_root_dir)
    test_root_dir = f"{test_root_dir}/{test_resource_name}"
    print(f"Setting up test folder {test_root_dir}")
    shutil.copytree("../dbt-project-template", test_root_dir)
    copy_replace("../dbt-project-template/dbt_project.yml", os.path.join(test_root_dir, "dbt_project.yml"))
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
    return run_destination_process("", test_root_dir, commands)


def generate_dbt_models(destination_type: DestinationType, test_root_dir: str, column_count: int):
    """
    This is the normalization step generating dbt models files from the destination_catalog.json taken as input.
    """
    output_directory = os.path.join(test_root_dir, "models", "generated")
    shutil.rmtree(output_directory, ignore_errors=True)
    catalog_processor = CatalogProcessor(output_directory, destination_type)
    catalog_config = {
        "streams": [
            {
                "stream": {
                    "name": f"stream_with_{column_count}_columns",
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
        for column in [random_string(5) for _ in range(column_count)]:
            catalog_config["streams"][0]["stream"]["json_schema"]["properties"][column] = {"type": "string"}
    catalog = os.path.join(test_root_dir, "catalog.json")
    with open(catalog, "w") as fh:
        fh.write(json.dumps(catalog_config))
    catalog_processor.process(catalog, "_airbyte_data", target_schema)
