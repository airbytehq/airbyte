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


import os

import pytest
from normalization.transform_catalog.transform import extract_schema
from normalization.transform_config.transform import DestinationType, TransformConfig


class TestTransformConfig:
    """
    This class is testing the transform config functionality that converts a destination_config.json into the adequate profiles.yml file for dbt to use
    """

    @pytest.fixture(scope="class", autouse=True)
    def before_all_tests(self, request):
        # This makes the test run whether it is executed from the tests folder (with pytest/gradle)
        # or from the base-normalization folder (through pycharm)
        unit_tests_dir = os.path.join(request.fspath.dirname, "unit_tests")
        if os.path.exists(unit_tests_dir):
            os.chdir(unit_tests_dir)
        else:
            os.chdir(request.fspath.dirname)
        yield
        os.chdir(request.config.invocation_dir)

    def test_transform_bigquery(self):
        input = {"project_id": "my_project_id", "dataset_id": "my_dataset_id", "credentials_json": '{ "type": "service_account-json" }'}

        actual_output = TransformConfig().transform_bigquery(input)
        expected_output = {
            "type": "bigquery",
            "method": "service-account-json",
            "project": "my_project_id",
            "dataset": "my_dataset_id",
            "keyfile_json": {"type": "service_account-json"},
            "retries": 1,
            "threads": 32,
        }

        actual_keyfile = actual_output["keyfile_json"]
        expected_keyfile = {"type": "service_account-json"}
        assert expected_output == actual_output
        assert expected_keyfile == actual_keyfile
        assert extract_schema(actual_output) == "my_dataset_id"

    def test_transform_bigquery_no_credentials(self):
        input = {"project_id": "my_project_id", "dataset_id": "my_dataset_id"}

        actual_output = TransformConfig().transform_bigquery(input)
        expected_output = {
            "type": "bigquery",
            "method": "oauth",
            "project": "my_project_id",
            "dataset": "my_dataset_id",
            "retries": 1,
            "threads": 32,
        }

        assert expected_output == actual_output
        assert extract_schema(actual_output) == "my_dataset_id"

    def test_transform_postgres(self):
        input = {
            "host": "airbyte.io",
            "port": 5432,
            "username": "a user",
            "password": "password123",
            "database": "my_db",
            "schema": "public",
        }

        actual = TransformConfig().transform_postgres(input)
        expected = {
            "type": "postgres",
            "dbname": "my_db",
            "host": "airbyte.io",
            "pass": "password123",
            "port": 5432,
            "schema": "public",
            "threads": 32,
            "user": "a user",
        }

        assert expected == actual
        assert extract_schema(actual) == "public"

    def test_transform_snowflake(self):
        input = {
            "host": "http://123abc.us-east-7.aws.snowflakecomputing.com",
            "role": "AIRBYTE_ROLE",
            "warehouse": "AIRBYTE_WAREHOUSE",
            "database": "AIRBYTE_DATABASE",
            "schema": "AIRBYTE_SCHEMA",
            "username": "AIRBYTE_USER",
            "password": "password123",
        }

        actual = TransformConfig().transform_snowflake(input)
        expected = {
            "account": "123abc.us-east-7.aws",
            "client_session_keep_alive": False,
            "database": "AIRBYTE_DATABASE",
            "password": "password123",
            "query_tag": "normalization",
            "role": "AIRBYTE_ROLE",
            "schema": "AIRBYTE_SCHEMA",
            "threads": 32,
            "type": "snowflake",
            "user": "AIRBYTE_USER",
            "warehouse": "AIRBYTE_WAREHOUSE",
        }

        assert expected == actual
        assert extract_schema(actual) == "AIRBYTE_SCHEMA"

    def test_transform_mysql(self):
        input = {
            "type": "mysql5",
            "host": "airbyte.io",
            "port": 5432,
            "database": "my_db",
            "schema": "public",
            "username": "a user",
            "password": "password1234",
        }

        actual = TransformConfig().transform_mysql(input)
        expected = {
            "type": "mysql5",
            "server": "airbyte.io",
            "port": 5432,
            "schema": "my_db",
            "database": "my_db",
            "username": "a user",
            "password": "password1234",
        }

        assert expected == actual
        # DBT schema is equivalent to MySQL database
        assert extract_schema(actual) == "my_db"

    # test that the full config is produced. this overlaps slightly with the transform_postgres test.
    def test_transform(self):
        input = {
            "host": "airbyte.io",
            "port": 5432,
            "username": "a user",
            "password": "password123",
            "database": "my_db",
            "schema": "public",
        }

        expected = self.get_base_config()
        expected["normalize"]["outputs"]["prod"] = {
            "type": "postgres",
            "dbname": "my_db",
            "host": "airbyte.io",
            "pass": "password123",
            "port": 5432,
            "schema": "public",
            "threads": 32,
            "user": "a user",
        }
        actual = TransformConfig().transform(DestinationType.postgres, input)

        assert expected == actual
        assert extract_schema(actual["normalize"]["outputs"]["prod"]) == "public"

    def get_base_config(self):
        return {
            "config": {
                "partial_parse": True,
                "printer_width": 120,
                "send_anonymous_usage_stats": False,
                "use_colors": True,
            },
            "normalize": {"target": "prod", "outputs": {"prod": {}}},
        }

    def test_parse(self):
        t = TransformConfig()
        assert {"integration_type": DestinationType.postgres, "config": "config.json", "output_path": "out.yml"} == t.parse(
            ["--integration-type", "postgres", "--config", "config.json", "--out", "out.yml"]
        )
