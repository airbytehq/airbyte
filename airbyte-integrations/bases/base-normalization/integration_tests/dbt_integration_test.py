#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
import os
import pathlib
import random
import re
import socket
import string
import subprocess
import sys
import threading
import time
from copy import copy
from typing import Any, Callable, Dict, List, Union

import yaml
from normalization.destination_type import DestinationType
from normalization.transform_catalog.transform import read_yaml_config, write_yaml_config
from normalization.transform_config.transform import TransformConfig

NORMALIZATION_TEST_TARGET = "NORMALIZATION_TEST_TARGET"
NORMALIZATION_TEST_MSSQL_DB_PORT = "NORMALIZATION_TEST_MSSQL_DB_PORT"
NORMALIZATION_TEST_MYSQL_DB_PORT = "NORMALIZATION_TEST_MYSQL_DB_PORT"
NORMALIZATION_TEST_POSTGRES_DB_PORT = "NORMALIZATION_TEST_POSTGRES_DB_PORT"
NORMALIZATION_TEST_CLICKHOUSE_DB_PORT = "NORMALIZATION_TEST_CLICKHOUSE_DB_PORT"
NORMALIZATION_TEST_CLICKHOUSE_DB_TCP_PORT = "NORMALIZATION_TEST_CLICKHOUSE_DB_TCP_PORT"


class DbtIntegrationTest(object):
    def __init__(self):
        self.target_schema = "test_normalization"
        self.container_prefix = f"test_normalization_db_{self.random_string(3)}"
        self.db_names = []

    @staticmethod
    def generate_random_string(prefix: str) -> str:
        return prefix + DbtIntegrationTest.random_string(5)

    @staticmethod
    def random_string(length: int) -> str:
        return "".join(random.choice(string.ascii_lowercase) for i in range(length))

    def set_target_schema(self, target_schema: str):
        self.target_schema = target_schema

    def setup_db(self, destinations_to_test: List[str]):
        if DestinationType.POSTGRES.value in destinations_to_test:
            self.setup_postgres_db()
        if DestinationType.MYSQL.value in destinations_to_test:
            self.setup_mysql_db()
        if DestinationType.MSSQL.value in destinations_to_test:
            self.setup_mssql_db()
        if DestinationType.CLICKHOUSE.value in destinations_to_test:
            self.setup_clickhouse_db()

    def setup_postgres_db(self):
        start_db = True
        if os.getenv(NORMALIZATION_TEST_POSTGRES_DB_PORT):
            port = int(os.getenv(NORMALIZATION_TEST_POSTGRES_DB_PORT))
            start_db = False
        else:
            port = self.find_free_port()
        config = {
            "host": "localhost",
            "username": "integration-tests",
            "password": "integration-tests",
            "port": port,
            "database": "postgres",
            "schema": self.target_schema,
        }
        if start_db:
            self.db_names.append("postgres")
            print("Starting localhost postgres container for tests")
            commands = [
                "docker",
                "run",
                "--rm",
                "--name",
                f"{self.container_prefix}_postgres",
                "-e",
                f"POSTGRES_USER={config['username']}",
                "-e",
                f"POSTGRES_PASSWORD={config['password']}",
                "-p",
                f"{config['port']}:5432",
                "-d",
                "marcosmarxm/postgres-ssl:dev",
                "-c",
                "ssl=on",
                "-c",
                "ssl_cert_file=/var/lib/postgresql/server.crt",
                "-c",
                "ssl_key_file=/var/lib/postgresql/server.key",
            ]
            print("Executing: ", " ".join(commands))
            subprocess.call(commands)
            print("....Waiting for Postgres DB to start...15 sec")
            time.sleep(15)
        if not os.path.exists("../secrets"):
            os.makedirs("../secrets")
        with open("../secrets/postgres.json", "w") as fh:
            fh.write(json.dumps(config))

    def setup_mysql_db(self):
        start_db = True
        if os.getenv(NORMALIZATION_TEST_MYSQL_DB_PORT):
            port = int(os.getenv(NORMALIZATION_TEST_MYSQL_DB_PORT))
            start_db = False
        else:
            port = self.find_free_port()
        config = {
            "host": "localhost",
            "port": port,
            "database": self.target_schema,
            "username": "root",
            "password": "",
        }
        if start_db:
            self.db_names.append("mysql")
            print("Starting localhost mysql container for tests")
            commands = [
                "docker",
                "run",
                "--rm",
                "--name",
                f"{self.container_prefix}_mysql",
                "-e",
                "MYSQL_ALLOW_EMPTY_PASSWORD=yes",
                "-e",
                "MYSQL_INITDB_SKIP_TZINFO=yes",
                "-e",
                f"MYSQL_DATABASE={config['database']}",
                "-e",
                "MYSQL_ROOT_HOST=%",
                "-p",
                f"{config['port']}:3306",
                "-d",
                "mysql/mysql-server",
            ]
            print("Executing: ", " ".join(commands))
            subprocess.call(commands)
            print("....Waiting for MySQL DB to start...15 sec")
            time.sleep(15)
        if not os.path.exists("../secrets"):
            os.makedirs("../secrets")
        with open("../secrets/mysql.json", "w") as fh:
            fh.write(json.dumps(config))

    def setup_mssql_db(self):
        start_db = True
        if os.getenv(NORMALIZATION_TEST_MSSQL_DB_PORT):
            port = int(os.getenv(NORMALIZATION_TEST_MSSQL_DB_PORT))
            start_db = False
        else:
            port = self.find_free_port()
        config = {
            "host": "localhost",
            "username": "SA",
            "password": "MyStr0ngP@ssw0rd",
            "port": port,
            "database": self.target_schema,
            "schema": self.target_schema,
        }
        if start_db:
            self.db_names.append("mssql")
            print("Starting localhost MS SQL Server container for tests")
            command_start_container = [
                "docker",
                "run",
                "--rm",
                "--name",
                f"{self.container_prefix}_mssql",
                "-h",
                f"{self.container_prefix}_mssql",
                "-e",
                "ACCEPT_EULA='Y'",
                "-e",
                f"SA_PASSWORD='{config['password']}'",
                "-e",
                "MSSQL_PID='Standard'",
                "-p",
                f"{config['port']}:1433",
                "-d",
                "mcr.microsoft.com/mssql/server:2019-GA-ubuntu-16.04",
            ]
            # cmds & parameters
            cmd_start_container = " ".join(command_start_container)
            wait_sec = 30
            # run the docker container
            print("Executing: ", cmd_start_container)
            subprocess.check_call(cmd_start_container, shell=True)
            # wait for service is available
            print(f"....Waiting for MS SQL Server to start...{wait_sec} sec")
            time.sleep(wait_sec)
            # Run additional commands to prepare the table
            command_create_db = [
                "docker",
                "exec",
                f"{self.container_prefix}_mssql",
                "/opt/mssql-tools/bin/sqlcmd",
                "-S",
                config["host"],
                "-U",
                config["username"],
                "-P",
                config["password"],
                "-Q",
                f"CREATE DATABASE [{config['database']}]",
            ]
            # create test db
            print("Executing: ", " ".join(command_create_db))
            subprocess.call(command_create_db)
        if not os.path.exists("../secrets"):
            os.makedirs("../secrets")
        with open("../secrets/mssql.json", "w") as fh:
            fh.write(json.dumps(config))

    def setup_clickhouse_db(self):
        """
        ClickHouse official JDBC driver use HTTP port 8123, while Python ClickHouse
        driver uses native port 9000, so we need to open both ports for destination
        connector and dbt container respectively.

        Ref: https://altinity.com/blog/2019/3/15/clickhouse-networking-part-1
        """
        start_db = True
        port = 8123
        tcp_port = 9000
        if os.getenv(NORMALIZATION_TEST_CLICKHOUSE_DB_PORT):
            port = int(os.getenv(NORMALIZATION_TEST_CLICKHOUSE_DB_PORT))
            start_db = False
        if os.getenv(NORMALIZATION_TEST_CLICKHOUSE_DB_TCP_PORT):
            tcp_port = int(os.getenv(NORMALIZATION_TEST_CLICKHOUSE_DB_TCP_PORT))
            start_db = False
        if start_db:
            port = self.find_free_port()
            tcp_port = self.find_free_port()
        config = {
            "host": "localhost",
            "port": port,
            "tcp-port": tcp_port,
            "database": self.target_schema,
            "username": "default",
            "password": "",
            "ssl": False,
        }
        if start_db:
            self.db_names.append("clickhouse")
            print("Starting localhost clickhouse container for tests")
            commands = [
                "docker",
                "run",
                "--rm",
                "--name",
                f"{self.container_prefix}_clickhouse",
                "--ulimit",
                "nofile=262144:262144",
                "-p",
                f"{config['tcp-port']}:9000",  # Python clickhouse driver use native port
                "-p",
                f"{config['port']}:8123",  # clickhouse JDBC driver use HTTP port
                "-d",
                # so far, only the latest version ClickHouse server image turned on
                # window functions
                "clickhouse/clickhouse-server:latest",
            ]
            print("Executing: ", " ".join(commands))
            subprocess.call(commands)
            print("....Waiting for ClickHouse DB to start...15 sec")
            time.sleep(15)
        # Run additional commands to prepare the table
        command_create_db = [
            "docker",
            "run",
            "--rm",
            "--link",
            f"{self.container_prefix}_clickhouse:clickhouse-server",
            "clickhouse/clickhouse-client:21.8.10.19",
            "--host",
            "clickhouse-server",
            "--query",
            f"CREATE DATABASE IF NOT EXISTS {config['database']}",
        ]
        # create test db
        print("Executing: ", " ".join(command_create_db))
        subprocess.call(command_create_db)
        if not os.path.exists("../secrets"):
            os.makedirs("../secrets")
        with open("../secrets/clickhouse.json", "w") as fh:
            fh.write(json.dumps(config))

    @staticmethod
    def find_free_port():
        """
        Find an unused port to create a database listening on localhost to run destination-postgres
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 0))
        addr = s.getsockname()
        s.close()
        return addr[1]

    def tear_down_db(self):
        for db_name in self.db_names:
            print(f"Stopping localhost {db_name} container for tests")
            try:
                subprocess.call(["docker", "kill", f"{self.container_prefix}_{db_name}"])
            except Exception as e:
                print(f"WARN: Exception while shutting down {db_name}: {e}")

    @staticmethod
    def change_current_test_dir(request):
        # This makes the test run whether it is executed from the tests folder (with pytest/gradle)
        # or from the base-normalization folder (through pycharm)
        integration_tests_dir = os.path.join(request.fspath.dirname, "integration_tests")
        if os.path.exists(integration_tests_dir):
            os.chdir(integration_tests_dir)
        else:
            os.chdir(request.fspath.dirname)

    def generate_profile_yaml_file(
        self, destination_type: DestinationType, test_root_dir: str, random_schema: bool = False
    ) -> Dict[str, Any]:
        """
        Each destination requires different settings to connect to. This step generates the adequate profiles.yml
        as described here: https://docs.getdbt.com/reference/profiles.yml
        """
        config_generator = TransformConfig()
        profiles_config = config_generator.read_json_config(f"../secrets/{destination_type.value.lower()}.json")
        # Adapt credential file to look like destination config.json
        if destination_type.value == DestinationType.BIGQUERY.value:
            credentials = profiles_config["basic_bigquery_config"]
            profiles_config = {
                "credentials_json": json.dumps(credentials),
                "dataset_id": self.target_schema,
                "project_id": credentials["project_id"],
                "dataset_location": "US",
            }
        elif destination_type.value == DestinationType.MYSQL.value:
            profiles_config["database"] = self.target_schema
        elif destination_type.value == DestinationType.REDSHIFT.value:
            profiles_config["schema"] = self.target_schema
            if random_schema:
                profiles_config["schema"] = self.target_schema + "_" + "".join(random.choices(string.ascii_lowercase, k=5))
        else:
            profiles_config["schema"] = self.target_schema
        if destination_type.value == DestinationType.CLICKHOUSE.value:
            clickhouse_config = copy(profiles_config)
            profiles_yaml = config_generator.transform(destination_type, clickhouse_config)
        else:
            profiles_yaml = config_generator.transform(destination_type, profiles_config)
        config_generator.write_yaml_config(test_root_dir, profiles_yaml, "profiles.yml")
        return profiles_config

    @staticmethod
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
                            if not line.startswith(b"#"):
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

    @staticmethod
    def get_normalization_image(destination_type: DestinationType) -> str:
        if DestinationType.MSSQL.value == destination_type.value:
            return "airbyte/normalization-mssql:dev"
        elif DestinationType.MYSQL.value == destination_type.value:
            return "airbyte/normalization-mysql:dev"
        elif DestinationType.ORACLE.value == destination_type.value:
            return "airbyte/normalization-oracle:dev"
        elif DestinationType.CLICKHOUSE.value == destination_type.value:
            return "airbyte/normalization-clickhouse:dev"
        elif DestinationType.SNOWFLAKE.value == destination_type.value:
            return "airbyte/normalization-snowflake:dev"
        elif DestinationType.REDSHIFT.value == destination_type.value:
            return "airbyte/normalization-redshift:dev"
        else:
            return "airbyte/normalization:dev"

    def dbt_check(self, destination_type: DestinationType, test_root_dir: str):
        """
        Run the dbt CLI to perform transformations on the test raw data in the destination
        """
        normalization_image: str = self.get_normalization_image(destination_type)
        # Perform sanity check on dbt project settings
        assert self.run_check_dbt_command(normalization_image, "debug", test_root_dir)
        assert self.run_check_dbt_command(normalization_image, "deps", test_root_dir)

    def dbt_run(self, destination_type: DestinationType, test_root_dir: str, force_full_refresh: bool = False):
        """
        Run the dbt CLI to perform transformations on the test raw data in the destination
        """
        normalization_image: str = self.get_normalization_image(destination_type)
        # Compile dbt models files into destination sql dialect, then run the transformation queries
        assert self.run_check_dbt_command(normalization_image, "run", test_root_dir, force_full_refresh)

    def dbt_run_macro(self, destination_type: DestinationType, test_root_dir: str, macro: str, macro_args: str = None):
        """
        Run the dbt CLI to perform transformations on the test raw data in the destination, using independent macro.
        """
        normalization_image: str = self.get_normalization_image(destination_type)
        # Compile dbt models files into destination sql dialect, then run the transformation queries
        assert self.run_dbt_run_operation(normalization_image, test_root_dir, macro, macro_args)

    def run_check_dbt_command(self, normalization_image: str, command: str, cwd: str, force_full_refresh: bool = False) -> bool:
        """
        Run dbt subprocess while checking and counting for "ERROR", "FAIL" or "WARNING" printed in its outputs
        """
        if normalization_image.startswith("airbyte/normalization-oracle"):
            dbtAdditionalArgs = []
        else:
            dbtAdditionalArgs = ["--event-buffer-size=10000"]

        commands = (
            [
                "docker",
                "run",
                "--rm",
                "--init",
                "-v",
                f"{cwd}:/workspace",
                "-v",
                f"{cwd}/build:/build",
                "-v",
                f"{cwd}/logs:/logs",
                "-v",
                f"{cwd}/build/dbt_packages:/dbt",
                "--network",
                "host",
                "--entrypoint",
                "/usr/local/bin/dbt",
                "-i",
                normalization_image,
            ]
            + dbtAdditionalArgs
            + [
                command,
                "--profiles-dir=/workspace",
                "--project-dir=/workspace",
            ]
        )
        if force_full_refresh:
            commands.append("--full-refresh")
            command = f"{command} --full-refresh"
        print("Executing: ", " ".join(commands))
        print(f"Equivalent to: dbt {command} --profiles-dir={cwd} --project-dir={cwd}")
        return self.run_check_dbt_subprocess(commands, cwd)

    def run_dbt_run_operation(self, normalization_image: str, cwd: str, macro: str, macro_args: str = None) -> bool:
        """
        Run dbt subprocess while checking and counting for "ERROR", "FAIL" or "WARNING" printed in its outputs
        """
        args = ["--args", macro_args] if macro_args else []
        commands = (
            [
                "docker",
                "run",
                "--rm",
                "--init",
                "-v",
                f"{cwd}:/workspace",
                "-v",
                f"{cwd}/build:/build",
                "-v",
                f"{cwd}/logs:/logs",
                "-v",
                f"{cwd}/build/dbt_packages:/dbt",
                "--network",
                "host",
                "--entrypoint",
                "/usr/local/bin/dbt",
                "-i",
                normalization_image,
            ]
            + ["run-operation", macro]
            + args
            + ["--profiles-dir=/workspace", "--project-dir=/workspace"]
        )

        print("Executing: ", " ".join(commands))
        print(f"Equivalent to: dbt run-operation {macro} --args {macro_args} --profiles-dir={cwd} --project-dir={cwd}")
        return self.run_check_dbt_subprocess(commands, cwd)

    def run_check_dbt_subprocess(self, commands: list, cwd: str):
        error_count = 0
        with open(os.path.join(cwd, "dbt_output.log"), "ab") as f:
            process = subprocess.Popen(commands, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=os.environ)
            for line in iter(lambda: process.stdout.readline(), b""):
                f.write(line)
                str_line = line.decode("utf-8")
                sys.stdout.write(str_line)
                # keywords to match lines as signaling errors
                if "ERROR" in str_line or "FAIL" in str_line or "WARNING" in str_line:
                    # exception keywords in lines to ignore as errors (such as summary or expected warnings)
                    is_exception = False
                    for except_clause in [
                        "Done.",  # DBT Summary
                        "PASS=",  # DBT Summary
                        "Nothing to do.",  # When no schema/data tests are setup
                        "Configuration paths exist in your dbt_project.yml",  # When no cte / view are generated
                        "Error loading config file: .dockercfg: $HOME is not defined",  # ignore warning
                        "depends on a node named 'disabled_test' which was not found",  # Tests throwing warning because it is disabled
                        "The requested image's platform (linux/amd64) does not match the detected host platform "
                        + "(linux/arm64/v8) and no specific platform was requested",  # temporary patch until we publish images for arm64
                    ]:
                        if except_clause in str_line:
                            is_exception = True
                            break
                    if not is_exception:
                        # count lines signaling an error/failure/warning
                        error_count += 1
        process.wait()
        message = (
            f"{' '.join(commands)}\n\tterminated with return code {process.returncode} "
            f"with {error_count} 'Error/Warning/Fail' mention(s)."
        )
        print(message)
        assert error_count == 0, message
        assert process.returncode == 0, message
        if error_count > 0:
            return False
        return process.returncode == 0

    @staticmethod
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

    @staticmethod
    def get_test_targets() -> List[str]:
        """
        Returns a list of destinations to run tests on.

        if the environment variable NORMALIZATION_TEST_TARGET is set with a comma separated list of destination names,
        then the tests are run only on that subsets of destinations
        Otherwise tests are run against all destinations
        """
        if os.getenv(NORMALIZATION_TEST_TARGET):
            target_str = os.getenv(NORMALIZATION_TEST_TARGET)
            return [d.value for d in {DestinationType.from_string(s.strip()) for s in target_str.split(",")}]
        else:
            return [d.value for d in DestinationType]

    @staticmethod
    def update_yaml_file(filename: str, callback: Callable):
        config = read_yaml_config(filename)
        updated, config = callback(config)
        if updated:
            write_yaml_config(config, filename)

    def clean_tmp_tables(
        self,
        destination_type: Union[DestinationType, List[DestinationType]],
        test_type: str,
        tmp_folders: list = None,
        git_versioned_tests: list = None,
    ):
        """
        Cleans-up all temporary schemas created during the test session.
        It parses the provided tmp_folders: List[str] or uses `git_versioned_tests` to find sources.yml files generated for the tests.
        It gets target schemas created by the tests and removes them using custom scenario specified in
            `dbt-project-template/macros/clean_tmp_tables.sql` macro.

        REQUIREMENTS:
        1) Idealy, the schemas should have unique names like: test_normalization_<some_random_string> to avoid conflicts.
        2) The `clean_tmp_tables.sql` macro should have the specific macro for target destination to proceed.

        INPUT ARGUMENTS:
        ::  destination_type : either single destination or list of destinations
        ::  test_type: either "ephemeral" or "normalization" should be supplied.
        ::  tmp_folders: should be supplied if test_type = "ephemeral", to get schemas from /build/normalization_test_output folders
        ::  git_versioned_tests: should be supplied if test_type = "normalization", to get schemas from integration_tests/normalization_test_output folders

        EXAMPLE:
            clean_up_args = {
                "destination_type": [ DestinationType.REDSHIFT, DestinationType.POSTGRES, ... ]
                "test_type": "normalization",
                "git_versioned_tests": git_versioned_tests,
            }
        """

        path_to_sources: str = "/models/generated/sources.yml"
        test_folders: dict = {}
        source_files: dict = {}
        schemas_to_remove: dict = {}

        # collecting information about tmp_tables created for the test for each destination
        for destination in destination_type:
            test_folders[destination.value] = []
            source_files[destination.value] = []
            schemas_to_remove[destination.value] = []

            # based on test_type select path to source files
            if test_type == "ephemeral":
                if not tmp_folders:
                    raise TypeError("`tmp_folders` arg is not provided.")
                for folder in tmp_folders:
                    if destination.value in folder:
                        test_folders[destination.value].append(folder)
                        source_files[destination.value].append(f"{folder}{path_to_sources}")
            elif test_type == "normalization":
                if not git_versioned_tests:
                    raise TypeError("`git_versioned_tests` arg is not provided.")
                base_path = f"{pathlib.Path().absolute()}/integration_tests/normalization_test_output"
                for test in git_versioned_tests:
                    test_root_dir: str = f"{base_path}/{destination.value}/{test}"
                    test_folders[destination.value].append(test_root_dir)
                    source_files[destination.value].append(f"{test_root_dir}{path_to_sources}")
            else:
                raise TypeError(f"\n`test_type`: {test_type} is not a registered, use `ephemeral` or `normalization` instead.\n")

            # parse source.yml files from test folders to get schemas and table names created for the tests
            for file in source_files[destination.value]:
                source_yml = {}
                try:
                    with open(file, "r") as source_file:
                        source_yml = yaml.safe_load(source_file)
                except FileNotFoundError:
                    print(f"\n{destination.value}: {file} doesn't exist, consider to remove any temp_tables and schemas manually!\n")
                    pass
                test_sources: list = source_yml.get("sources", []) if source_yml else []

                for source in test_sources:
                    target_schema: str = source.get("name")
                    if target_schema not in schemas_to_remove[destination.value]:
                        schemas_to_remove[destination.value].append(target_schema)
                        # adding _airbyte_* tmp schemas to be removed
                        schemas_to_remove[destination.value].append(f"_airbyte_{target_schema}")

        # cleaning up tmp_tables generated by the tests
        for destination in destination_type:
            if not schemas_to_remove[destination.value]:
                print(f"\n\t{destination.value.upper()} DESTINATION: SKIP CLEANING, NOTHING TO REMOVE.\n")
            else:
                print(f"\n\t{destination.value.upper()} DESTINATION: CLEANING LEFTOVERS...\n")
                print(f"\t{schemas_to_remove[destination.value]}\n")
                test_root_folder = test_folders[destination.value][0]
                args = json.dumps({"schemas": schemas_to_remove[destination.value]})
                self.dbt_check(destination, test_root_folder)
                self.dbt_run_macro(destination, test_root_folder, "clean_tmp_tables", args)
