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
import random
import re
import shutil
import socket
import string
import subprocess
import sys
import tempfile
import threading
from typing import Any, Dict, List

import pytest
from normalization.destination_type import DestinationType
from normalization.transform_catalog.catalog_processor import CatalogProcessor
from normalization.transform_config.transform import TransformConfig

temporary_folders = set()
target_schema = "test_normalization"
container_name = "test_normalization_db_" + "".join(random.choice(string.ascii_lowercase) for i in range(3))

# dbt models and final sql outputs from the following git versioned tests will be written in a folder included in
# airbyte git repository.
git_versioned_tests = ["test_primary_key_streams"]


@pytest.fixture(scope="package", autouse=True)
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


@pytest.mark.parametrize(
    "test_resource_name",
    set(
        git_versioned_tests
        + [
            # Non-versioned tests outputs below will be written to /tmp folders instead
        ]
    ),
)
@pytest.mark.parametrize(
    "integration_type",
    [
        "Postgres",
        "BigQuery",
        "Snowflake",
        "Redshift",
    ],
)
def test_normalization(integration_type: str, test_resource_name: str, setup_test_path):
    print("Testing normalization")
    destination_type = DestinationType.from_string(integration_type)
    # Create the test folder with dbt project and appropriate destination settings to run integration tests from
    test_root_dir = setup_test_dir(integration_type, test_resource_name)
    destination_config = generate_profile_yaml_file(destination_type, test_root_dir)
    # Use destination connector to create _airbyte_raw_* tables to use as input for the test
    assert setup_input_raw_data(integration_type, test_resource_name, test_root_dir, destination_config)
    # Normalization step
    generate_dbt_models(destination_type, test_resource_name, test_root_dir)
    dbt_run(test_root_dir)
    # Run checks on Tests results
    dbt_test(destination_type, test_resource_name, test_root_dir)
    check_outputs(destination_type, test_resource_name, test_root_dir)


def setup_postgres_db():
    print("Starting localhost postgres container for tests")
    port = find_free_port()
    config = {
        "host": "localhost",
        "username": "integration-tests",
        "password": "integration-tests",
        "port": port,
        "database": "postgres",
        "schema": target_schema,
    }
    commands = [
        "docker",
        "run",
        "--rm",
        "--name",
        f"{container_name}",
        "-e",
        f"POSTGRES_USER={config['username']}",
        "-e",
        f"POSTGRES_PASSWORD={config['password']}",
        "-p",
        f"{config['port']}:5432",
        "-d",
        "postgres",
    ]
    print("Executing: ", " ".join(commands))
    subprocess.call(commands)
    if not os.path.exists("../secrets"):
        os.makedirs("../secrets")
    with open("../secrets/postgres.json", "w") as fh:
        fh.write(json.dumps(config))


def find_free_port():
    """
    Find an unused port to create a database listening on localhost to run destination-postgres
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    addr = s.getsockname()
    s.close()
    return addr[1]


def tear_down_postgres_db():
    print("Stopping localhost postgres container for tests")
    try:
        subprocess.call(["docker", "kill", f"{container_name}"])
        os.remove("../secrets/postgres.json")
    except Exception as e:
        print(f"WARN: Exception while shutting down postgres db: {e}")


def change_current_test_dir(request):
    # This makes the test run whether it is executed from the tests folder (with pytest/gradle) or from the base-normalization folder (through pycharm)
    integration_tests_dir = os.path.join(request.fspath.dirname, "integration_tests")
    if os.path.exists(integration_tests_dir):
        os.chdir(integration_tests_dir)
    else:
        os.chdir(request.fspath.dirname)


def setup_test_dir(integration_type: str, test_resource_name: str) -> str:
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
        test_root_dir = f"{pathlib.Path().absolute()}/normalization_test_output/{integration_type.lower()}"
    else:
        test_root_dir = tempfile.mkdtemp(dir="/tmp/", prefix="normalization_test_", suffix=f"_{integration_type.lower()}")
        temporary_folders.add(test_root_dir)
    shutil.rmtree(test_root_dir, ignore_errors=True)
    os.makedirs(test_root_dir)
    test_root_dir = f"{test_root_dir}/{test_resource_name}"
    print(f"Setting up test folder {test_root_dir}")
    shutil.copytree("../dbt-project-template", test_root_dir)
    if integration_type != "Redshift":
        # Prefer 'view' to 'ephemeral' for tests so it's easier to debug with dbt
        copy_replace(
            "../dbt-project-template/dbt_project.yml",
            os.path.join(test_root_dir, "dbt_project.yml"),
            pattern="ephemeral",
            replace_value="view",
        )
    else:
        # 'view' materializations on redshift are too slow, so keep it ephemeral there...
        copy_replace("../dbt-project-template/dbt_project.yml", os.path.join(test_root_dir, "dbt_project.yml"))
    return test_root_dir


def generate_profile_yaml_file(destination_type: DestinationType, test_root_dir: str) -> Dict[str, Any]:
    """
    Each destination requires different settings to connect to. This step generates the adequate profiles.yml
    as described here: https://docs.getdbt.com/reference/profiles.yml
    """
    config_generator = TransformConfig()
    profiles_config = config_generator.read_json_config(f"../secrets/{destination_type.value.lower()}.json")
    # Adapt credential file to look like destination config.json
    if destination_type.value == DestinationType.BIGQUERY.value:
        profiles_config["credentials_json"] = json.dumps(profiles_config)
        profiles_config["dataset_id"] = target_schema
    else:
        profiles_config["schema"] = target_schema
    profiles_yaml = config_generator.transform(destination_type, profiles_config)
    config_generator.write_yaml_config(test_root_dir, profiles_yaml)
    return profiles_config


def setup_input_raw_data(integration_type: str, test_resource_name: str, test_root_dir: str, destination_config: Dict[str, Any]) -> bool:
    """
    We run docker images of destinations to upload test data stored in the messages.txt file for each test case.
    This should populate the associated "raw" tables from which normalization is reading from when running dbt CLI.
    """
    catalog_file = os.path.join("resources", test_resource_name, "data_input", "catalog.json")
    message_file = os.path.join("resources", test_resource_name, "data_input", "messages.txt")
    copy_replace(
        catalog_file,
        os.path.join(test_root_dir, "reset_catalog.json"),
        pattern='"destination_sync_mode": ".*"',
        replace_value='"destination_sync_mode": "overwrite"',
    )
    copy_replace(catalog_file, os.path.join(test_root_dir, "destination_catalog.json"))
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
    ]
    # Force a reset in destination raw tables
    assert run_destination_process("", test_root_dir, commands + ["/data/reset_catalog.json"])
    # Run a sync to create raw tables in destinations
    return run_destination_process(message_file, test_root_dir, commands + ["/data/destination_catalog.json"])


def run_destination_process(message_file: str, test_root_dir: str, commands: List[str]):
    print("Executing: ", " ".join(commands))
    with open(os.path.join(test_root_dir, "destination_output.log"), "ab") as f:
        process = subprocess.Popen(commands, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        def writer():
            if os.path.exists(message_file):
                with open(message_file, "rb") as input_data:
                    while True:
                        line = input_data.readline()
                        if not line:
                            break
                        process.stdin.write(line)
            process.stdin.close()

        thread = threading.Thread(target=writer)
        thread.start()
        for line in iter(process.stdout.readline, b""):
            f.write(line)
            sys.stdout.write(line.decode("utf-8"))
        thread.join()
        process.wait()
    return process.returncode == 0


def generate_dbt_models(destination_type: DestinationType, test_resource_name: str, test_root_dir: str):
    """
    This is the normalization step generating dbt models files from the destination_catalog.json taken as input.
    """
    catalog_processor = CatalogProcessor(os.path.join(test_root_dir, "models", "generated"), destination_type)
    catalog_processor.process(os.path.join("resources", test_resource_name, "data_input", "catalog.json"), "_airbyte_data", target_schema)


def dbt_run(test_root_dir: str):
    """
    Run the dbt CLI to perform transformations on the test raw data in the destination
    """
    # Perform sanity check on dbt project settings
    assert run_check_dbt_command("debug", test_root_dir)
    final_sql_files = os.path.join(test_root_dir, "final")
    shutil.rmtree(final_sql_files, ignore_errors=True)
    # Compile dbt models files into destination sql dialect, then run the transformation queries
    dbt_run_succeeded = run_check_dbt_command("run", test_root_dir)
    # Copy final SQL files to persist them in git
    # shutil.copytree(os.path.join(test_root_dir, "..", "build", "run", "airbyte_utils", "models", "generated"), final_sql_files)
    assert dbt_run_succeeded


def dbt_test(destination_type: DestinationType, test_resource_name: str, test_root_dir: str):
    """
    dbt provides a way to run dbt tests as described here: https://docs.getdbt.com/docs/building-a-dbt-project/tests
    - Schema tests are added in .yml files from the schema_tests directory
        - see additional macros for testing here: https://github.com/fishtown-analytics/dbt-utils#schema-tests
    - Data tests are added in .sql files from the data_tests directory and should return 0 records to be successful

    We use this mechanism to verify the output of our integration tests.
    """
    replace_identifiers = os.path.join("resources", test_resource_name, "data_input", "replace_identifiers.json")
    copy_test_files(
        os.path.join("resources", test_resource_name, "dbt_schema_tests"),
        os.path.join(test_root_dir, "models/dbt_schema_tests"),
        destination_type,
        replace_identifiers,
    )
    copy_test_files(
        os.path.join("resources", test_resource_name, "dbt_data_tests"),
        os.path.join(test_root_dir, "tests"),
        destination_type,
        replace_identifiers,
    )
    assert run_check_dbt_command("test", test_root_dir)


def run_check_dbt_command(command: str, cwd: str) -> bool:
    """
    Run dbt subprocess while checking and counting for "ERROR", "FAIL" or "WARNING" printed in its outputs
    """
    error_count = 0
    commands = [
        "docker",
        "run",
        "--rm",
        "--init",
        "-v",
        f"{cwd}:/workspace",
        "-v",
        f"{cwd}/build:/build",
        "-v",
        f"{cwd}/final:/build/run/airbyte_utils/models/generated",
        "-v",
        "/tmp/bq_keyfile.json:/tmp/bq_keyfile.json",
        "--network",
        "host",
        "--entrypoint",
        "/usr/local/bin/dbt",
        "-i",
        "airbyte/normalization:dev",
        command,
        "--profiles-dir=/workspace",
        "--project-dir=/workspace",
    ]
    print("Executing: ", " ".join(commands))
    print(f"Equivalent to: dbt {command} --profiles-dir={cwd} --project-dir={cwd}")
    with open(os.path.join(cwd, "dbt_output.log"), "ab") as f:
        process = subprocess.Popen(commands, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=os.environ)
        for line in iter(process.stdout.readline, b""):
            f.write(line)
            str_line = line.decode("utf-8")
            sys.stdout.write(str_line)
            # keywords to match lines as signaling errors
            if "ERROR" in str_line or "FAIL" in str_line or "WARNING" in str_line:
                # exception keywords in lines to ignore as errors (such as summary or expected warnings)
                if not (
                    "Done." in str_line  # DBT Summary
                    or "PASS=" in str_line  # DBT Summary
                    or "Nothing to do." in str_line  # When no schema/data tests are setup
                    or "Configuration paths exist in your dbt_project.yml"  # When catalog does not generate a view or cte
                ):
                    # count lines signaling an error/failure/warning
                    error_count += 1
    process.wait()
    print(f"{' '.join(commands)}\n\tterminated with return code {process.returncode} with {error_count} 'ERROR' mention(s).")
    if error_count > 0:
        return False
    return process.returncode == 0


def check_outputs(destination_type: DestinationType, test_resource_name: str, test_root_dir: str):
    """
    Implement other types of checks on the output directory (grepping, diffing files etc?)
    """
    print("Checking test outputs")


def copy_replace(src, dst, pattern=None, replace_value=None):
    """
    Copies a file from src to dst replacing pattern by replace_value
    Parameters
    ----------
    src : string
        Path to the source filename to copy from
    dst : string
        Path to the output filename to copy to
    pattern
        list of Patterns to replace inside the src file
    replace_value
        list of Values to replace by in the dst file
    """
    file1 = open(src, "r") if isinstance(src, str) else src
    file2 = open(dst, "w") if isinstance(dst, str) else dst
    pattern = [pattern] if isinstance(pattern, str) else pattern
    replace_value = [replace_value] if isinstance(replace_value, str) else replace_value
    if replace_value and pattern:
        if len(replace_value) != len(pattern):
            raise Exception("Invalid parameters: pattern and replace_value" " have different sizes.")
        rules = [(re.compile(regex, re.IGNORECASE), value) for regex, value in zip(pattern, replace_value)]
    else:
        rules = []
    for line in file1:
        if rules:
            for rule in rules:
                line = re.sub(rule[0], rule[1], line)
        file2.write(line)
    if isinstance(src, str):
        file1.close()
    if isinstance(dst, str):
        file2.close()


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
            if destination_type.value in identifiers_map:
                for entry in identifiers_map[destination_type.value]:
                    for k in entry:
                        pattern.append(k)
                        replace_value.append(entry[k])
            if pattern and replace_value:

                def copy_replace_identifiers(src, dst):
                    copy_replace(src, dst, pattern, replace_value)

                shutil.copytree(src, temp_dir + "/replace", copy_function=copy_replace_identifiers)
                src = temp_dir + "/replace"
        # final copy
        shutil.copytree(src, dst)


def copy_upper(src, dst):
    print(src, "->", dst)
    copy_replace(
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
    copy_replace(
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
