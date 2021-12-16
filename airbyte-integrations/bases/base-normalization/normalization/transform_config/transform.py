#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import argparse
import json
import os
import pkgutil
import socket
from enum import Enum
from typing import Any, Dict

import yaml


class DestinationType(Enum):
    bigquery = "bigquery"
    postgres = "postgres"
    redshift = "redshift"
    snowflake = "snowflake"
    mysql = "mysql"
    oracle = "oracle"
    mssql = "mssql"
    clickhouse = "clickhouse"


class TransformConfig:
    def run(self, args):
        inputs = self.parse(args)
        original_config = self.read_json_config(inputs["config"])
        integration_type = inputs["integration_type"]
        transformed_config = self.transform(integration_type, original_config)
        self.write_yaml_config(inputs["output_path"], transformed_config, "profiles.yml")
        if self.is_ssh_tunnelling(original_config):
            self.write_ssh_config(inputs["output_path"], original_config, transformed_config)

    @staticmethod
    def parse(args):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--config", type=str, required=True, help="path to original config")
        parser.add_argument(
            "--integration-type", type=DestinationType, choices=list(DestinationType), required=True, help="type of integration"
        )
        parser.add_argument("--out", type=str, required=True, help="path to output transformed config to")

        parsed_args = parser.parse_args(args)
        print(str(parsed_args))

        return {
            "config": parsed_args.config,
            "integration_type": parsed_args.integration_type,
            "output_path": parsed_args.out,
        }

    def transform(self, integration_type: DestinationType, config: Dict[str, Any]):
        data = pkgutil.get_data(self.__class__.__module__.split(".")[0], "transform_config/profile_base.yml")
        if not data:
            raise FileExistsError("Failed to load profile_base.yml")
        base_profile = yaml.load(data, Loader=yaml.FullLoader)

        transformed_integration_config = {
            DestinationType.bigquery.value: self.transform_bigquery,
            DestinationType.postgres.value: self.transform_postgres,
            DestinationType.redshift.value: self.transform_redshift,
            DestinationType.snowflake.value: self.transform_snowflake,
            DestinationType.mysql.value: self.transform_mysql,
            DestinationType.oracle.value: self.transform_oracle,
            DestinationType.mssql.value: self.transform_mssql,
            DestinationType.clickhouse.value: self.transform_clickhouse,
        }[integration_type.value](config)

        # merge pre-populated base_profile with destination-specific configuration.
        base_profile["normalize"]["outputs"]["prod"] = transformed_integration_config

        return base_profile

    @staticmethod
    def is_ssh_tunnelling(config: Dict[str, Any]) -> bool:
        tunnel_methods = ["SSH_KEY_AUTH", "SSH_PASSWORD_AUTH"]
        if (
            "tunnel_method" in config.keys()
            and "tunnel_method" in config["tunnel_method"]
            and config["tunnel_method"]["tunnel_method"].upper() in tunnel_methods
        ):
            return True
        else:
            return False

    @staticmethod
    def is_port_free(port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("localhost", port))
            except Exception as e:
                print(f"port {port} unsuitable: {e}")
                return False
            else:
                print(f"port {port} is free")
                return True

    @staticmethod
    def pick_a_port() -> int:
        """
        This function finds a free port, starting with 50001 and adding 1 until we find an open port.
        """
        port_to_check = 50001  # just past start of dynamic port range (49152:65535)
        while not TransformConfig.is_port_free(port_to_check):
            port_to_check += 1
            # error if we somehow hit end of port range
            if port_to_check > 65535:
                raise RuntimeError("Couldn't find a free port to use.")
        return port_to_check

    @staticmethod
    def get_ssh_altered_config(config: Dict[str, Any], port_key: str = "port", host_key: str = "host") -> Dict[str, Any]:
        """
        This should be called only if ssh tunneling is on.
        It will return config with appropriately altered port and host values
        """
        # make a copy of config rather than mutate in place
        ssh_ready_config = {k: v for k, v in config.items()}
        ssh_ready_config[port_key] = TransformConfig.pick_a_port()
        ssh_ready_config[host_key] = "localhost"
        return ssh_ready_config

    @staticmethod
    def transform_bigquery(config: Dict[str, Any]):
        print("transform_bigquery")
        # https://docs.getdbt.com/reference/warehouse-profiles/bigquery-profile
        dbt_config = {
            "type": "bigquery",
            "project": config["project_id"],
            "dataset": config["dataset_id"],
            "priority": config.get("transformation_priority", "interactive"),
            "threads": 32,
            "retries": 1,
        }
        if "credentials_json" in config:
            dbt_config["method"] = "service-account-json"
            dbt_config["keyfile_json"] = json.loads(config["credentials_json"])
        else:
            dbt_config["method"] = "oauth"
        if "dataset_location" in config:
            dbt_config["location"] = config["dataset_location"]
        return dbt_config

    @staticmethod
    def transform_postgres(config: Dict[str, Any]):
        print("transform_postgres")

        if TransformConfig.is_ssh_tunnelling(config):
            config = TransformConfig.get_ssh_altered_config(config, port_key="port", host_key="host")

        # https://docs.getdbt.com/reference/warehouse-profiles/postgres-profile
        dbt_config = {
            "type": "postgres",
            "host": config["host"],
            "user": config["username"],
            "pass": config.get("password", ""),
            "port": config["port"],
            "dbname": config["database"],
            "schema": config["schema"],
            "threads": 32,
        }

        # if unset, we assume true.
        if config.get("ssl", True):
            config["sslmode"] = "require"

        return dbt_config

    @staticmethod
    def transform_redshift(config: Dict[str, Any]):
        print("transform_redshift")
        # https://docs.getdbt.com/reference/warehouse-profiles/redshift-profile
        dbt_config = {
            "type": "redshift",
            "host": config["host"],
            "user": config["username"],
            "pass": config["password"],
            "port": config["port"],
            "dbname": config["database"],
            "schema": config["schema"],
            "threads": 32,
        }
        return dbt_config

    @staticmethod
    def transform_snowflake(config: Dict[str, Any]):
        print("transform_snowflake")
        # here account is everything before ".snowflakecomputing.com" as it can include account, region & cloud environment information)
        account = config["host"].replace(".snowflakecomputing.com", "").replace("http://", "").replace("https://", "")
        # https://docs.getdbt.com/reference/warehouse-profiles/snowflake-profile
        # snowflake coerces most of these values to uppercase, but if dbt has them as a different casing it has trouble finding the resources it needs. thus we coerce them to upper.
        dbt_config = {
            "type": "snowflake",
            "account": account,
            "user": config["username"].upper(),
            "password": config["password"],
            "role": config["role"].upper(),
            "database": config["database"].upper(),
            "warehouse": config["warehouse"].upper(),
            "schema": config["schema"].upper(),
            "threads": 32,
            "client_session_keep_alive": False,
            "query_tag": "normalization",
        }
        return dbt_config

    @staticmethod
    def transform_mysql(config: Dict[str, Any]):
        print("transform_mysql")

        if TransformConfig.is_ssh_tunnelling(config):
            config = TransformConfig.get_ssh_altered_config(config, port_key="port", host_key="host")

        # https://github.com/dbeatty10/dbt-mysql#configuring-your-profile
        dbt_config = {
            # MySQL 8.x - type: mysql
            # MySQL 5.x - type: mysql5
            "type": config.get("type", "mysql"),
            "server": config["host"],
            "port": config["port"],
            # DBT schema is equivalent to MySQL database
            "schema": config["database"],
            "database": config["database"],
            "username": config["username"],
            "password": config.get("password", ""),
        }
        return dbt_config

    @staticmethod
    def transform_oracle(config: Dict[str, Any]):
        print("transform_oracle")
        # https://github.com/techindicium/dbt-oracle#configure-your-profile
        dbt_config = {
            "type": "oracle",
            "host": config["host"],
            "user": config["username"],
            "pass": config["password"],
            "port": config["port"],
            "dbname": config["sid"],
            "schema": config["schema"],
            "threads": 4,
        }
        return dbt_config

    @staticmethod
    def transform_mssql(config: Dict[str, Any]):
        print("transform_mssql")
        # https://docs.getdbt.com/reference/warehouse-profiles/mssql-profile
        dbt_config = {
            "type": "sqlserver",
            "driver": "ODBC Driver 17 for SQL Server",
            "server": config["host"],
            "port": config["port"],
            "schema": config["schema"],
            "database": config["database"],
            "user": config["username"],
            "password": config["password"],
            "threads": 32,
            # "authentication": "sql",
            # "trusted_connection": True,
        }
        return dbt_config

    @staticmethod
    def transform_clickhouse(config: Dict[str, Any]):
        print("transform_clickhouse")
        # https://docs.getdbt.com/reference/warehouse-profiles/clickhouse-profile
        dbt_config = {
            "type": "clickhouse",
            "host": config["host"],
            "port": config["port"],
            "schema": config["database"],
            "user": config["username"],
            "password": config["password"],
        }
        return dbt_config

    @staticmethod
    def read_json_config(input_path: str):
        with open(input_path, "r") as file:
            contents = file.read()
        return json.loads(contents)

    @staticmethod
    def write_yaml_config(output_path: str, config: Dict[str, Any], filename: str):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        with open(os.path.join(output_path, filename), "w") as fh:
            fh.write(yaml.dump(config))

    @staticmethod
    def write_ssh_config(output_path: str, original_config: Dict[str, Any], transformed_config: Dict[str, Any]):
        """
        This function writes a json file with config specific to ssh.
        We do this because we need these details to open the ssh tunnel for dbt.
        """
        ssh_dict = {
            "db_host": original_config["host"],
            "db_port": original_config["port"],
            "tunnel_map": original_config["tunnel_method"],
            "local_port": transformed_config["normalize"]["outputs"]["prod"]["port"],
        }
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        with open(os.path.join(output_path, "ssh.json"), "w") as fh:
            json.dump(ssh_dict, fh)


def main(args=None):
    TransformConfig().run(args)
