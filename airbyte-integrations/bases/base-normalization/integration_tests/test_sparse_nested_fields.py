#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
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
from integration_tests.utils import generate_dbt_models, run_destination_process
from normalization.destination_type import DestinationType

# from normalization.transform_catalog import TransformCatalog

temporary_folders = set()

# dbt models and final sql outputs from the following git versioned tests will be written in a folder included in
# airbyte git repository.
git_versioned_tests = ["test_simple_streams", "test_nested_streams"]

dbt_test_utils = DbtIntegrationTest()


@pytest.fixture(scope="module", autouse=True)
def before_all_tests(request):
    destinations_to_test = dbt_test_utils.get_test_targets()
    # set clean-up args to clean target destination after the test
    clean_up_args = {
        "destination_type": [d for d in DestinationType if d.value in destinations_to_test],
        "test_type": "normalization",
        "git_versioned_tests": git_versioned_tests,
    }
    for integration_type in [d.value for d in DestinationType]:
        if integration_type in destinations_to_test:
            test_root_dir = f"{pathlib.Path().absolute()}/normalization_test_output/{integration_type.lower()}"
            shutil.rmtree(test_root_dir, ignore_errors=True)
    if os.getenv("RANDOM_TEST_SCHEMA"):
        target_schema = dbt_test_utils.generate_random_string("test_normalization_ci_")
        dbt_test_utils.set_target_schema(target_schema)
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


@pytest.mark.parametrize("destination_type", DestinationType.testable_destinations())
def test_sparse_nested_fields(destination_type: DestinationType):
    # TODO extract these conditions?
    if destination_type.value not in dbt_test_utils.get_test_targets():
        pytest.skip(f"Destinations {destination_type} is not in NORMALIZATION_TEST_TARGET env variable")
    if (destination_type.value in (DestinationType.ORACLE.value, DestinationType.CLICKHOUSE.value)):
        pytest.skip(f"Destinations {destination_type} does not support nested streams")
    if destination_type.value in [DestinationType.MYSQL.value, DestinationType.ORACLE.value]:
        pytest.skip(f"{destination_type} does not support incremental yet")

    target_schema = dbt_test_utils.target_schema
    if destination_type.value == DestinationType.ORACLE.value:
        # Oracle does not allow changing to random schema
        dbt_test_utils.set_target_schema("test_normalization")
    elif destination_type.value == DestinationType.REDSHIFT.value:
        # set unique schema for Redshift test
        dbt_test_utils.set_target_schema(dbt_test_utils.generate_random_string("test_normalization_"))

    try:
        print(f"Testing sparse nested field normalization {destination_type} in ", dbt_test_utils.target_schema)
        test_resource_name = "test_sparse_nested_streams"

        # Create the test folder with dbt project and appropriate destination settings to run integration tests from
        test_root_dir = setup_test_dir(destination_type, test_resource_name)

        # First sync
        destination_config = dbt_test_utils.generate_profile_yaml_file(destination_type, test_root_dir)
        assert setup_input_raw_data(destination_type, test_resource_name, test_root_dir, destination_config)
        generate_dbt_models(destination_type, test_resource_name, test_root_dir, "models", "catalog.json", dbt_test_utils)
        dbt_test_utils.dbt_check(destination_type, test_root_dir)
        setup_dbt_sparse_nested_streams_test(destination_type, test_resource_name, test_root_dir, 1)
        dbt_test_utils.dbt_run(destination_type, test_root_dir)
        copy_tree(os.path.join(test_root_dir, "build/run/airbyte_utils/models/generated/"), os.path.join(test_root_dir, "sync1_output"))
        shutil.rmtree(os.path.join(test_root_dir, "build/run/airbyte_utils/models/generated/"), ignore_errors=True)
        dbt_test(destination_type, test_root_dir)

        # Second sync
        message_file = os.path.join("resources", test_resource_name, "data_input", "messages2.txt")
        assert run_destination_process(destination_type, test_root_dir, message_file, "destination_catalog.json", dbt_test_utils)
        setup_dbt_sparse_nested_streams_test(destination_type, test_resource_name, test_root_dir, 2)
        dbt_test_utils.dbt_run(destination_type, test_root_dir)
        copy_tree(os.path.join(test_root_dir, "build/run/airbyte_utils/models/generated/"), os.path.join(test_root_dir, "sync2_output"))
        shutil.rmtree(os.path.join(test_root_dir, "build/run/airbyte_utils/models/generated/"), ignore_errors=True)
        dbt_test(destination_type, test_root_dir)

        # Third sync
        message_file = os.path.join("resources", test_resource_name, "data_input", "messages3.txt")
        assert run_destination_process(destination_type, test_root_dir, message_file, "destination_catalog.json", dbt_test_utils)
        setup_dbt_sparse_nested_streams_test(destination_type, test_resource_name, test_root_dir, 3)
        dbt_test_utils.dbt_run(destination_type, test_root_dir)
        copy_tree(os.path.join(test_root_dir, "build/run/airbyte_utils/models/generated/"), os.path.join(test_root_dir, "sync3_output"))
        shutil.rmtree(os.path.join(test_root_dir, "build/run/airbyte_utils/models/generated/"), ignore_errors=True)
        dbt_test(destination_type, test_root_dir)
    finally:
        dbt_test_utils.set_target_schema(target_schema)
        clean_up_args = {
            "destination_type": [destination_type],
            "test_type": "ephemeral",
            "tmp_folders": [str(test_root_dir)],
        }
        dbt_test_utils.clean_tmp_tables(**clean_up_args)


def setup_test_dir(destination_type: DestinationType, test_resource_name: str) -> str:
    """
    We prepare a clean folder to run the tests from.

    if the test_resource_name is part of git_versioned_tests, then dbt models and final sql outputs
    will be written to a folder included in airbyte git repository.

    Non-versioned tests will be written in /tmp folders instead.

    The purpose is to keep track of a small set of downstream changes on selected integration tests cases.
     - generated dbt models created by normalization script from an input destination_catalog.json
     - final output sql files created by dbt CLI from the generated dbt models (dbt models are sql files with jinja templating,
     these are interpreted and compiled into the native SQL dialect of the final destination engine)
    """
    if test_resource_name in git_versioned_tests:
        test_root_dir = f"{pathlib.Path().absolute()}/normalization_test_output/{destination_type.value.lower()}"
    else:
        test_root_dir = f"{pathlib.Path().joinpath('..', 'build', 'normalization_test_output', destination_type.value.lower()).resolve()}"
    os.makedirs(test_root_dir, exist_ok=True)
    test_root_dir = f"{test_root_dir}/{test_resource_name}"
    shutil.rmtree(test_root_dir, ignore_errors=True)
    print(f"Setting up test folder {test_root_dir}")
    dbt_project_yaml = "../dbt-project-template/dbt_project.yml"
    copy_tree("../dbt-project-template", test_root_dir)
    if destination_type.value == DestinationType.MSSQL.value:
        copy_tree("../dbt-project-template-mssql", test_root_dir)
        dbt_project_yaml = "../dbt-project-template-mssql/dbt_project.yml"
    elif destination_type.value == DestinationType.MYSQL.value:
        copy_tree("../dbt-project-template-mysql", test_root_dir)
        dbt_project_yaml = "../dbt-project-template-mysql/dbt_project.yml"
    elif destination_type.value == DestinationType.ORACLE.value:
        copy_tree("../dbt-project-template-oracle", test_root_dir)
        dbt_project_yaml = "../dbt-project-template-oracle/dbt_project.yml"
    elif destination_type.value == DestinationType.CLICKHOUSE.value:
        copy_tree("../dbt-project-template-clickhouse", test_root_dir)
        dbt_project_yaml = "../dbt-project-template-clickhouse/dbt_project.yml"
    elif destination_type.value == DestinationType.SNOWFLAKE.value:
        copy_tree("../dbt-project-template-snowflake", test_root_dir)
        dbt_project_yaml = "../dbt-project-template-snowflake/dbt_project.yml"
    elif destination_type.value == DestinationType.REDSHIFT.value:
        copy_tree("../dbt-project-template-redshift", test_root_dir)
        dbt_project_yaml = "../dbt-project-template-redshift/dbt_project.yml"
    elif destination_type.value == DestinationType.TIDB.value:
        copy_tree("../dbt-project-template-tidb", test_root_dir)
        dbt_project_yaml = "../dbt-project-template-tidb/dbt_project.yml"
    elif destination_type.value == DestinationType.DUCKDB.value:
        copy_tree("../dbt-project-template-duckdb", test_root_dir)
        dbt_project_yaml = "../dbt-project-template-duckdb/dbt_project.yml"
    dbt_test_utils.copy_replace(dbt_project_yaml, os.path.join(test_root_dir, "dbt_project.yml"))
    return test_root_dir


def setup_input_raw_data(
    destination_type: DestinationType, test_resource_name: str, test_root_dir: str, destination_config: Dict[str, Any]
) -> bool:
    """
    We run docker images of destinations to upload test data stored in the messages.txt file for each test case.
    This should populate the associated "raw" tables from which normalization is reading from when running dbt CLI.
    """
    catalog_file = os.path.join("resources", test_resource_name, "data_input", "catalog.json")
    message_file = os.path.join("resources", test_resource_name, "data_input", "messages.txt")
    dbt_test_utils.copy_replace(
        catalog_file,
        os.path.join(test_root_dir, "reset_catalog.json"),
        pattern='"destination_sync_mode": ".*"',
        replace_value='"destination_sync_mode": "overwrite"',
    )
    dbt_test_utils.copy_replace(catalog_file, os.path.join(test_root_dir, "destination_catalog.json"))
    config_file = os.path.join(test_root_dir, "destination_config.json")
    with open(config_file, "w") as f:
        f.write(json.dumps(destination_config))
    # Force a reset in destination raw tables
    assert run_destination_process(destination_type, test_root_dir, "", "reset_catalog.json", dbt_test_utils)
    # Run a sync to create raw tables in destinations
    return run_destination_process(destination_type, test_root_dir, message_file, "destination_catalog.json", dbt_test_utils)


def setup_dbt_sparse_nested_streams_test(destination_type: DestinationType, test_resource_name: str, test_root_dir: str, sync_number: int):
    """
    Prepare the data (copy) for the models for dbt test.
    """
    replace_identifiers = os.path.join("resources", test_resource_name, "data_input", "replace_identifiers.json")
    test_directory = os.path.join(test_root_dir, "models/dbt_data_tests")
    shutil.rmtree(test_directory, ignore_errors=True)
    os.makedirs(test_directory, exist_ok=True)
    copy_test_files(
        os.path.join("resources", test_resource_name, "dbt_test_config", f"sync{sync_number}_expectations"),
        test_directory,
        destination_type,
        replace_identifiers,
    )
    test_directory = os.path.join(test_root_dir, "tests")
    shutil.rmtree(test_directory, ignore_errors=True)
    os.makedirs(test_directory, exist_ok=True)
    copy_test_files(
        os.path.join("resources", test_resource_name, "dbt_test_config", f"sync{sync_number}_assertions"),
        test_directory,
        destination_type,
        replace_identifiers,
    )


def dbt_test(destination_type: DestinationType, test_root_dir: str):
    """
    dbt provides a way to run dbt tests as described here: https://docs.getdbt.com/docs/building-a-dbt-project/tests
    - Schema tests are added in .yml files from the schema_tests directory
        - see additional macros for testing here: https://github.com/fishtown-analytics/dbt-utils#schema-tests
    - Data tests are added in .sql files from the data_tests directory and should return 0 records to be successful

    We use this mechanism to verify the output of our integration tests.
    """
    normalization_image: str = dbt_test_utils.get_normalization_image(destination_type)
    assert dbt_test_utils.run_check_dbt_command(normalization_image, "test", test_root_dir)


def copy_test_files(src: str, dst: str, destination_type: DestinationType, replace_identifiers: str):
    """
    Copy file while hacking snowflake identifiers that needs to be uppercased...
    (so we can share these dbt tests files accross destinations)
    """
    if os.path.exists(src):
        temp_dir = tempfile.mkdtemp(dir="/tmp/", prefix="normalization_test_")
        temporary_folders.add(temp_dir)
        # Copy and adapt capitalization
        if destination_type.value == DestinationType.SNOWFLAKE.value:
            shutil.copytree(src, temp_dir + "/upper", copy_function=copy_upper)
            src = temp_dir + "/upper"
        elif destination_type.value == DestinationType.REDSHIFT.value:
            shutil.copytree(src, temp_dir + "/lower", copy_function=copy_lower)
            src = temp_dir + "/lower"
        if os.path.exists(replace_identifiers):
            with open(replace_identifiers, "r") as file:
                contents = file.read()
            identifiers_map = json.loads(contents)
            pattern = []
            replace_value = []
            if dbt_test_utils.target_schema != "test_normalization":
                pattern.append("test_normalization")
                if destination_type.value == DestinationType.SNOWFLAKE.value:
                    replace_value.append(dbt_test_utils.target_schema.upper())
                else:
                    replace_value.append(dbt_test_utils.target_schema)
            if destination_type.value in identifiers_map:
                for entry in identifiers_map[destination_type.value]:
                    for k in entry:
                        # re.escape() must not be used for the replacement string in sub(), only backslashes should be escaped:
                        # see https://docs.python.org/3/library/re.html#re.escape
                        pattern.append(k.replace("\\", r"\\"))
                        replace_value.append(entry[k])
            if pattern and replace_value:

                def copy_replace_identifiers(src, dst):
                    dbt_test_utils.copy_replace(src, dst, pattern, replace_value)

                shutil.copytree(src, temp_dir + "/replace", copy_function=copy_replace_identifiers)
                src = temp_dir + "/replace"
        # final copy
        copy_tree(src, dst)


def copy_upper(src, dst):
    print(src, "->", dst)
    dbt_test_utils.copy_replace(
        src,
        dst,
        pattern=[
            r"(- name:) *(.*)",
            r"(ref\(')(.*)('\))",
            r"(source\(')(.*)('\))",
        ],
        replace_value=[
            to_upper_identifier,
            to_upper_identifier,
            to_upper_identifier,
        ],
    )


def copy_lower(src, dst):
    print(src, "->", dst)
    dbt_test_utils.copy_replace(
        src,
        dst,
        pattern=[
            r"(- name:) *(.*)",
            r"(ref\(')(.*)('\))",
            r"(source\(')(.*)('\))",
        ],
        replace_value=[
            to_lower_identifier,
            to_lower_identifier,
            to_lower_identifier,
        ],
    )


def to_upper_identifier(input: re.Match) -> str:
    if len(input.groups()) == 2:
        return f"{input.group(1)} {input.group(2).upper()}"
    elif len(input.groups()) == 3:
        return f"{input.group(1)}{input.group(2).upper()}{input.group(3)}"
    else:
        raise Exception(f"Unexpected number of groups in {input}")


def to_lower_identifier(input: re.Match) -> str:
    if len(input.groups()) == 2:
        return f"{input.group(1)} {input.group(2).lower()}"
    elif len(input.groups()) == 3:
        return f"{input.group(1)}{input.group(2).lower()}{input.group(3)}"
    else:
        raise Exception(f"Unexpected number of groups in {input}")
