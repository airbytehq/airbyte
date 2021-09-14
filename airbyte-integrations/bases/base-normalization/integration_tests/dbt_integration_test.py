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
import random
import re
import shutil
import socket
import string
import subprocess
import sys
import threading
import time
from typing import Any, Dict, List

from normalization.destination_type import DestinationType
from normalization.transform_config.transform import TransformConfig


class DbtIntegrationTest(object):
    def __init__(self):
        self.target_schema = "test_normalization"
        self.container_prefix = f"test_normalization_db_{self.random_string(3)}"
        self.db_names = ["postgres", "mysql"]

    @staticmethod
    def random_string(length: int) -> str:
        return "".join(random.choice(string.ascii_lowercase) for i in range(length))

    def setup_db(self):
        self.setup_postgres_db()
        self.setup_mysql_db()

    def setup_postgres_db(self):
        print("Starting localhost postgres container for tests")
        port = self.find_free_port()
        config = {
            "host": "localhost",
            "username": "integration-tests",
            "password": "integration-tests",
            "port": port,
            "database": "postgres",
            "schema": self.target_schema,
        }
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
            "postgres",
        ]
        print("Executing: ", " ".join(commands))
        subprocess.call(commands)
        time.sleep(5)

        if not os.path.exists("../secrets"):
            os.makedirs("../secrets")
        with open("../secrets/postgres.json", "w") as fh:
            fh.write(json.dumps(config))

    def setup_mysql_db(self):
        print("Starting localhost mysql container for tests")
        port = self.find_free_port()
        config = {
            "host": "localhost",
            "port": port,
            "database": self.target_schema,
            "username": "root",
            "password": "",
        }
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
        time.sleep(5)

        if not os.path.exists("../secrets"):
            os.makedirs("../secrets")
        with open("../secrets/mysql.json", "w") as fh:
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

    def generate_project_yaml_file(self, destination_type: DestinationType, test_root_dir: str) -> Dict[str, Any]:
        config_generator = TransformConfig()
        project_yaml = config_generator.transform_dbt_project(destination_type)
        config_generator.write_yaml_config(test_root_dir, project_yaml, "dbt_project.yml")
        return project_yaml

    def generate_profile_yaml_file(self, destination_type: DestinationType, test_root_dir: str) -> Dict[str, Any]:
        """
        Each destination requires different settings to connect to. This step generates the adequate profiles.yml
        as described here: https://docs.getdbt.com/reference/profiles.yml
        """
        config_generator = TransformConfig()
        profiles_config = config_generator.read_json_config(f"../secrets/{destination_type.value.lower()}.json")
        # Adapt credential file to look like destination config.json
        if destination_type.value == DestinationType.BIGQUERY.value:
            credentials = profiles_config
            profiles_config = {
                "credentials_json": json.dumps(credentials),
                "dataset_id": self.target_schema,
                "project_id": credentials["project_id"],
            }
        elif destination_type.value == DestinationType.MYSQL.value:
            profiles_config["database"] = self.target_schema
        else:
            profiles_config["schema"] = self.target_schema
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

    def dbt_run(self, test_root_dir: str):
        """
        Run the dbt CLI to perform transformations on the test raw data in the destination
        """
        # Perform sanity check on dbt project settings
        assert self.run_check_dbt_command("debug", test_root_dir)
        assert self.run_check_dbt_command("deps", test_root_dir)
        final_sql_files = os.path.join(test_root_dir, "final")
        shutil.rmtree(final_sql_files, ignore_errors=True)
        # Compile dbt models files into destination sql dialect, then run the transformation queries
        assert self.run_check_dbt_command("run", test_root_dir)

    @staticmethod
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
            "/tmp:/tmp",
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
