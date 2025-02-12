#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import os
import socket
import tempfile
import time

import pytest
from normalization.destination_type import DestinationType
from normalization.transform_catalog.transform import extract_path, extract_schema
from normalization.transform_config.transform import TransformConfig


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

    def test_is_ssh_tunnelling(self):
        def single_test(config, expected_output):
            assert TransformConfig.is_ssh_tunnelling(config) == expected_output

        inputs = [
            ({}, False),
            (
                {
                    "type": "postgres",
                    "dbname": "my_db",
                    "host": "airbyte.io",
                    "pass": "password123",
                    "port": 5432,
                    "schema": "public",
                    "threads": 32,
                    "user": "a user",
                },
                False,
            ),
            (
                {
                    "type": "postgres",
                    "dbname": "my_db",
                    "host": "airbyte.io",
                    "pass": "password123",
                    "port": 5432,
                    "schema": "public",
                    "threads": 32,
                    "user": "a user",
                    "tunnel_method": {
                        "tunnel_host": "1.2.3.4",
                        "tunnel_method": "SSH_PASSWORD_AUTH",
                        "tunnel_port": 22,
                        "tunnel_user": "user",
                        "tunnel_user_password": "pass",
                    },
                },
                True,
            ),
            (
                {
                    "type": "postgres",
                    "dbname": "my_db",
                    "host": "airbyte.io",
                    "pass": "password123",
                    "port": 5432,
                    "schema": "public",
                    "threads": 32,
                    "user": "a user",
                    "tunnel_method": {
                        "tunnel_method": "SSH_KEY_AUTH",
                    },
                },
                True,
            ),
            (
                {
                    "type": "postgres",
                    "dbname": "my_db",
                    "host": "airbyte.io",
                    "pass": "password123",
                    "port": 5432,
                    "schema": "public",
                    "threads": 32,
                    "user": "a user",
                    "tunnel_method": {
                        "nothing": "nothing",
                    },
                },
                False,
            ),
        ]
        for input_tuple in inputs:
            single_test(input_tuple[0], input_tuple[1])

    def test_is_port_free(self):
        # to test that this accurately identifies 'free' ports, we'll find a 'free' port and then try to use it
        test_port = 13055
        while not TransformConfig.is_port_free(test_port):
            test_port += 1
            if test_port > 65535:
                raise RuntimeError("couldn't find a free port...")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("localhost", test_port))
            # if we haven't failed then we accurately identified a 'free' port.
            # now we can test for accurate identification of 'in-use' port since we're using it
            assert TransformConfig.is_port_free(test_port) is False

        # and just for good measure now that our context manager is closed (and port open again)
        time.sleep(1)
        assert TransformConfig.is_port_free(test_port) is True

    def test_pick_a_port(self):
        supposedly_open_port = TransformConfig.pick_a_port()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("localhost", supposedly_open_port))

    def test_transform_bigquery(self):
        input = {
            "project_id": "my_project_id",
            "dataset_id": "my_dataset_id",
            "credentials_json": '{ "type": "service_account-json" }',
            "transformation_priority": "interactive",
            "dataset_location": "EU",
        }

        actual_output = TransformConfig().transform_bigquery(input)
        expected_output = {
            "type": "bigquery",
            "method": "service-account-json",
            "project": "my_project_id",
            "dataset": "my_dataset_id",
            "priority": "interactive",
            "keyfile_json": {"type": "service_account-json"},
            "location": "EU",
            "retries": 3,
            "threads": 8,
        }

        actual_keyfile = actual_output["keyfile_json"]
        expected_keyfile = {"type": "service_account-json"}
        assert actual_output == expected_output
        assert actual_keyfile == expected_keyfile
        assert extract_schema(actual_output) == "my_dataset_id"

    def test_transform_bigquery_no_credentials(self):
        input = {"project_id": "my_project_id", "dataset_id": "my_dataset_id"}

        actual_output = TransformConfig().transform_bigquery(input)
        expected_output = {
            "type": "bigquery",
            "method": "oauth",
            "project": "my_project_id",
            "dataset": "my_dataset_id",
            "priority": "interactive",
            "retries": 3,
            "threads": 8,
        }

        assert actual_output == expected_output
        assert extract_schema(actual_output) == "my_dataset_id"

    def test_transform_bigquery_with_embedded_project_id(self):
        input = {"project_id": "my_project_id", "dataset_id": "my_project_id:my_dataset_id"}

        actual_output = TransformConfig().transform_bigquery(input)
        expected_output = {
            "type": "bigquery",
            "method": "oauth",
            "project": "my_project_id",
            "dataset": "my_dataset_id",
            "priority": "interactive",
            "retries": 3,
            "threads": 8,
        }

        assert actual_output == expected_output
        assert extract_schema(actual_output) == "my_dataset_id"

    def test_transform_bigquery_with_embedded_mismatched_project_id(self):
        input = {"project_id": "my_project_id", "dataset_id": "bad_project_id:my_dataset_id"}

        try:
            TransformConfig().transform_bigquery(input)
            assert False, "transform_bigquery should have raised an exception"
        except ValueError:
            pass

    def test_transform_bigquery_with_invalid_format(self):
        input = {"project_id": "my_project_id", "dataset_id": "foo:bar:baz"}

        try:
            TransformConfig().transform_bigquery(input)
            assert False, "transform_bigquery should have raised an exception"
        except ValueError:
            pass

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
            "threads": 8,
            "user": "a user",
        }

        assert actual == expected
        assert extract_schema(actual) == "public"

    def test_transform_postgres_ssh(self):
        input = {
            "host": "airbyte.io",
            "port": 5432,
            "username": "a user",
            "password": "password123",
            "database": "my_db",
            "schema": "public",
            "tunnel_method": {
                "tunnel_host": "1.2.3.4",
                "tunnel_method": "SSH_PASSWORD_AUTH",
                "tunnel_port": 22,
                "tunnel_user": "user",
                "tunnel_user_password": "pass",
            },
        }
        port = TransformConfig.pick_a_port()

        actual = TransformConfig().transform_postgres(input)
        expected = {
            "type": "postgres",
            "dbname": "my_db",
            "host": "localhost",
            "pass": "password123",
            "port": port,
            "schema": "public",
            "threads": 8,
            "user": "a user",
        }

        assert actual == expected
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
            "threads": 5,
            "retry_all": True,
            "retry_on_database_errors": True,
            "connect_retries": 3,
            "connect_timeout": 15,
            "type": "snowflake",
            "user": "AIRBYTE_USER",
            "warehouse": "AIRBYTE_WAREHOUSE",
        }

        assert actual == expected
        assert extract_schema(actual) == "AIRBYTE_SCHEMA"

    def test_transform_snowflake_oauth(self):

        input = {
            "host": "http://123abc.us-east-7.aws.snowflakecomputing.com",
            "role": "AIRBYTE_ROLE",
            "warehouse": "AIRBYTE_WAREHOUSE",
            "database": "AIRBYTE_DATABASE",
            "schema": "AIRBYTE_SCHEMA",
            "username": "AIRBYTE_USER",
            "credentials": {
                "auth_type": "OAuth2.0",
                "client_id": "AIRBYTE_CLIENT_ID",
                "access_token": "AIRBYTE_ACCESS_TOKEN",
                "client_secret": "AIRBYTE_CLIENT_SECRET",
                "refresh_token": "AIRBYTE_REFRESH_TOKEN",
            },
        }

        actual = TransformConfig().transform_snowflake(input)
        expected = {
            "account": "123abc.us-east-7.aws",
            "client_session_keep_alive": False,
            "database": "AIRBYTE_DATABASE",
            "query_tag": "normalization",
            "role": "AIRBYTE_ROLE",
            "schema": "AIRBYTE_SCHEMA",
            "threads": 5,
            "retry_all": True,
            "retry_on_database_errors": True,
            "connect_retries": 3,
            "connect_timeout": 15,
            "type": "snowflake",
            "user": "AIRBYTE_USER",
            "warehouse": "AIRBYTE_WAREHOUSE",
            "authenticator": "oauth",
            "oauth_client_id": "AIRBYTE_CLIENT_ID",
            "oauth_client_secret": "AIRBYTE_CLIENT_SECRET",
            "token": "AIRBYTE_REFRESH_TOKEN",
        }

        assert actual == expected
        assert extract_schema(actual) == "AIRBYTE_SCHEMA"

    def test_transform_snowflake_key_pair(self):

        input = {
            "host": "http://123abc.us-east-7.aws.snowflakecomputing.com",
            "role": "AIRBYTE_ROLE",
            "warehouse": "AIRBYTE_WAREHOUSE",
            "database": "AIRBYTE_DATABASE",
            "schema": "AIRBYTE_SCHEMA",
            "username": "AIRBYTE_USER",
            "credentials": {
                "private_key": "AIRBYTE_PRIVATE_KEY",
                "private_key_password": "AIRBYTE_PRIVATE_KEY_PASSWORD",
            },
        }

        actual = TransformConfig().transform_snowflake(input)
        expected = {
            "account": "123abc.us-east-7.aws",
            "client_session_keep_alive": False,
            "database": "AIRBYTE_DATABASE",
            "query_tag": "normalization",
            "role": "AIRBYTE_ROLE",
            "schema": "AIRBYTE_SCHEMA",
            "threads": 5,
            "retry_all": True,
            "retry_on_database_errors": True,
            "connect_retries": 3,
            "connect_timeout": 15,
            "type": "snowflake",
            "user": "AIRBYTE_USER",
            "warehouse": "AIRBYTE_WAREHOUSE",
            "private_key_path": "private_key_path.txt",
            "private_key_passphrase": "AIRBYTE_PRIVATE_KEY_PASSWORD",
        }

        assert actual == expected
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

        assert actual == expected
        # DBT schema is equivalent to MySQL database
        assert extract_schema(actual) == "my_db"

    def test_transform_mssql(self):
        input = {
            "type": "sqlserver",
            "host": "airbyte.io",
            "port": 1433,
            "database": "my_db",
            "schema": "my_db",
            "username": "SA",
            "password": "password1234",
        }

        actual = TransformConfig().transform_mysql(input)
        expected = {
            "type": "sqlserver",
            "server": "airbyte.io",
            "port": 1433,
            "schema": "my_db",
            "database": "my_db",
            "username": "SA",
            "password": "password1234",
        }

        assert actual == expected
        # DBT schema is equivalent to MySQL database
        assert extract_schema(actual) == "my_db"

    def test_transform_clickhouse(self):
        input = {"host": "airbyte.io", "port": 9440, "database": "default", "username": "ch", "password": "password1234", "ssl": True}

        actual = TransformConfig().transform_clickhouse(input)
        expected = {
            "type": "clickhouse",
            "driver": "http",
            "verify": False,
            "host": "airbyte.io",
            "port": 9440,
            "schema": "default",
            "user": "ch",
            "password": "password1234",
            "secure": True,
        }

        assert actual == expected
        assert extract_schema(actual) == "default"

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
            "threads": 8,
            "user": "a user",
        }
        actual = TransformConfig().transform(DestinationType.POSTGRES, input)

        assert actual == expected
        assert extract_schema(actual["normalize"]["outputs"]["prod"]) == "public"

    def test_transform_tidb(self):
        input = {
            "type": "tidb",
            "host": "airbyte.io",
            "port": 5432,
            "database": "ti_db",
            "schema": "public",
            "username": "a user",
            "password": "password1234",
        }

        actual = TransformConfig().transform_tidb(input)
        expected = {
            "type": "tidb",
            "server": "airbyte.io",
            "port": 5432,
            "schema": "ti_db",
            "database": "ti_db",
            "username": "a user",
            "password": "password1234",
        }

        assert actual == expected
        assert extract_schema(actual) == "ti_db"

    def test_transform_duckdb_schema(self):
        input = {
            "type": "duckdb",
            "destination_path": "/local/testing.duckdb",
            "schema": "quackqauck",
        }

        actual = TransformConfig().transform_duckdb(input)
        expected = {
            "type": "duckdb",
            "path": "/local/testing.duckdb",
            "schema": "quackqauck",
        }

        assert actual == expected
        assert extract_path(actual) == "/local/testing.duckdb"

    def test_transform_duckdb_no_schema(self):
        input = {
            "type": "duckdb",
            "destination_path": "/local/testing.duckdb",
        }

        actual = TransformConfig().transform_duckdb(input)
        expected = {
            "type": "duckdb",
            "path": "/local/testing.duckdb",
            "schema": "main",
        }

        assert actual == expected
        assert extract_path(actual) == "/local/testing.duckdb"

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
        assert {"integration_type": DestinationType.POSTGRES, "config": "config.json", "output_path": "out.yml"} == t.parse(
            ["--integration-type", "postgres", "--config", "config.json", "--out", "out.yml"]
        )

    def test_write_ssh_config(self):
        original_config_input = {
            "type": "postgres",
            "dbname": "my_db",
            "host": "airbyte.io",
            "pass": "password123",
            "port": 5432,
            "schema": "public",
            "threads": 32,
            "user": "a user",
            "tunnel_method": {
                "tunnel_host": "1.2.3.4",
                "tunnel_method": "SSH_PASSWORD_AUTH",
                "tunnel_port": 22,
                "tunnel_user": "user",
                "tunnel_user_password": "pass",
            },
        }
        transformed_config_input = self.get_base_config()
        transformed_config_input["normalize"]["outputs"]["prod"] = {
            "port": 7890,
        }
        expected = {
            "db_host": "airbyte.io",
            "db_port": 5432,
            "tunnel_map": {
                "tunnel_host": "1.2.3.4",
                "tunnel_method": "SSH_PASSWORD_AUTH",
                "tunnel_port": 22,
                "tunnel_user": "user",
                "tunnel_user_password": "pass",
            },
            "local_port": 7890,
        }
        tmp_path = tempfile.TemporaryDirectory().name
        TransformConfig.write_ssh_config(tmp_path, original_config_input, transformed_config_input)
        with open(os.path.join(tmp_path, "ssh.json"), "r") as f:
            assert json.load(f) == expected
