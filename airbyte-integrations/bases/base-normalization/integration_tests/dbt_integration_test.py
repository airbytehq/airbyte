#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
import os
import random
import re
import socket
import string
import subprocess
import sys
import threading
import time
from copy import copy
from typing import Any, Callable, Dict, List

from normalization.destination_type import DestinationType
from normalization.transform_catalog.transform import read_yaml_config, write_yaml_config
from normalization.transform_config.transform import TransformConfig

NORMALIZATION_TEST_TARGET = "NORMALIZATION_TEST_TARGET"
NORMALIZATION_TEST_MSSQL_DB_PORT = "NORMALIZATION_TEST_MSSQL_DB_PORT"
NORMALIZATION_TEST_MYSQL_DB_PORT = "NORMALIZATION_TEST_MYSQL_DB_PORT"
NORMALIZATION_TEST_POSTGRES_DB_PORT = "NORMALIZATION_TEST_POSTGRES_DB_PORT"
NORMALIZATION_TEST_CLICKHOUSE_DB_PORT = "NORMALIZATION_TEST_CLICKHOUSE_DB_PORT"


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
                "-p",
                f"{config['port']}:3306",
                "-d",
                "mysql",
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
        if os.getenv(NORMALIZATION_TEST_CLICKHOUSE_DB_PORT):
            port = int(os.getenv(NORMALIZATION_TEST_CLICKHOUSE_DB_PORT))
            start_db = False
        else:
            port = self.find_free_port()
        config = {
            "host": "localhost",
            "port": port,
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
                "9000:9000",  # Python clickhouse driver use native port
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
            # Python ClickHouse driver uses native port 9000, which is different
            # from official ClickHouse JDBC driver
            clickhouse_config = copy(profiles_config)
            clickhouse_config["port"] = 9000
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

    @staticmethod
    def run_check_dbt_command(normalization_image: str, command: str, cwd: str, force_full_refresh: bool = False) -> bool:
        """
        Run dbt subprocess while checking and counting for "ERROR", "FAIL" or "WARNING" printed in its outputs
        """
        if normalization_image.startswith("airbyte/normalization-oracle") or normalization_image.startswith("airbyte/normalization-mysql"):
            dbtAdditionalArgs = []
        else:
            dbtAdditionalArgs = ["--event-buffer-size=10000"]

        error_count = 0
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
