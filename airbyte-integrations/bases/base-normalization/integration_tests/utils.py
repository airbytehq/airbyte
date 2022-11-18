#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import os
import pathlib
import shutil
import tempfile
from distutils.dir_util import copy_tree

from integration_tests.dbt_integration_test import DbtIntegrationTest
from normalization import DestinationType, TransformCatalog


def setup_test_dir(integration_type: str, temporary_folders: set) -> str:
    """
    We prepare a clean folder to run the tests from.
    """
    test_root_dir = f"{pathlib.Path().joinpath('..', 'build', 'normalization_test_output', integration_type.lower()).resolve()}"
    os.makedirs(test_root_dir, exist_ok=True)
    test_root_dir = tempfile.mkdtemp(dir=test_root_dir)
    temporary_folders.add(test_root_dir)
    shutil.rmtree(test_root_dir, ignore_errors=True)
    current_path = os.getcwd()
    print(f"Setting up test folder {test_root_dir}. Current path {current_path}")
    copy_tree("../dbt-project-template", test_root_dir)
    if integration_type == DestinationType.MSSQL.value:
        copy_tree("../dbt-project-template-mssql", test_root_dir)
    elif integration_type == DestinationType.MYSQL.value:
        copy_tree("../dbt-project-template-mysql", test_root_dir)
    elif integration_type == DestinationType.ORACLE.value:
        copy_tree("../dbt-project-template-oracle", test_root_dir)
    elif integration_type == DestinationType.SNOWFLAKE.value:
        copy_tree("../dbt-project-template-snowflake", test_root_dir)
    elif integration_type == DestinationType.TIDB.value:
        copy_tree("../dbt-project-template-tidb", test_root_dir)
    return test_root_dir


def run_destination_process(
    destination_type: DestinationType,
    test_root_dir: str,
    message_file: str,
    catalog_file: str,
    dbt_test_utils: DbtIntegrationTest,
    docker_tag="dev",
):
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
        f"airbyte/destination-{destination_type.value.lower()}:{docker_tag}",
        "write",
        "--config",
        "/data/destination_config.json",
        "--catalog",
    ]
    return dbt_test_utils.run_destination_process(message_file, test_root_dir, commands + [f"/data/{catalog_file}"])


def generate_dbt_models(
    destination_type: DestinationType,
    test_resource_name: str,
    test_root_dir: str,
    output_dir: str,
    catalog_file: str,
    dbt_test_utils: DbtIntegrationTest,
):
    """
    This is the normalization step generating dbt models files from the destination_catalog.json taken as input.
    """
    transform_catalog = TransformCatalog()
    transform_catalog.config = {
        "integration_type": destination_type.value,
        "schema": dbt_test_utils.target_schema,
        "catalog": [os.path.join("resources", test_resource_name, "data_input", catalog_file)],
        "output_path": os.path.join(test_root_dir, output_dir, "generated"),
        "json_column": "_airbyte_data",
        "profile_config_dir": test_root_dir,
    }
    transform_catalog.process_catalog()
