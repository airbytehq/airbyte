"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import argparse
import json
import pkgutil
from enum import Enum

import yaml


class DestinationType(Enum):
    bigquery = "bigquery"
    postgres = "postgres"
    snowflake = "snowflake"


class TransformConfig:
    def run(self, args):
        inputs = self.parse(args)
        original_config = self.read_json_config(inputs["config"])
        transformed_config = self.transform(inputs["integration_type"], original_config)

        self.write_yaml_config(inputs["output_path"], transformed_config)

    def parse(self, args):
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

    def transform(self, integration_type: DestinationType, config: dict):
        base_profile = yaml.load(
            pkgutil.get_data(self.__class__.__module__.split(".")[0], "transform_config/profile_base.yml"), Loader=yaml.FullLoader
        )

        transformed_integration_config = {
            DestinationType.bigquery: self.transform_bigquery,
            DestinationType.postgres: self.transform_postgres,
            DestinationType.snowflake: self.transform_snowflake,
        }[integration_type](config)

        # merge pre-populated base_profile with destination-specific configuration.
        base_profile["normalize"]["outputs"]["prod"] = transformed_integration_config

        return base_profile

    def transform_bigquery(self, config: dict):
        print("transform_bigquery")
        credentials_json = config["credentials_json"]
        keyfile_path = "/tmp/bq_keyfile.json"
        with open(keyfile_path, "w") as fh:
            fh.write(credentials_json)

        # https://docs.getdbt.com/reference/warehouse-profiles/bigquery-profile
        dbt_config = dict()
        dbt_config["type"] = "bigquery"
        dbt_config["method"] = "service-account"
        dbt_config["project"] = config["project_id"]
        dbt_config["dataset"] = config["dataset_id"]
        dbt_config["keyfile"] = keyfile_path
        dbt_config["threads"] = 32
        dbt_config["retries"] = 1

        return dbt_config

    def transform_postgres(self, config: dict):
        print("transform_postgres")
        dbt_config = dict()

        # https://docs.getdbt.com/reference/warehouse-profiles/postgres-profile
        dbt_config["type"] = "postgres"
        dbt_config["host"] = config["host"]
        dbt_config["user"] = config["username"]
        dbt_config["pass"] = config["password"]
        dbt_config["port"] = config["port"]
        dbt_config["dbname"] = config["database"]
        dbt_config["schema"] = config["schema"]
        dbt_config["threads"] = 32

        return dbt_config

    def transform_snowflake(self, config: dict):
        print("transform_snowflake")
        dbt_config = dict()

        # https://docs.getdbt.com/reference/warehouse-profiles/snowflake-profile
        dbt_config["type"] = "snowflake"
        # account is the first term subdomain of the host.
        dbt_config["account"] = config["host"].split(".")[0]
        dbt_config["user"] = config["username"]
        dbt_config["password"] = config["password"]
        dbt_config["role"] = config["role"]
        dbt_config["database"] = config["database"]
        dbt_config["warehouse"] = config["warehouse"]
        dbt_config["schema"] = config["schema"]
        dbt_config["threads"] = 32
        dbt_config["client_session_keep_alive"] = False
        dbt_config["query_tag"] = "normalization"

        return dbt_config

    def read_json_config(self, input_path: str):
        with open(input_path, "r") as file:
            contents = file.read()
        return json.loads(contents)

    def write_yaml_config(self, output_path: str, config: dict):
        with open(output_path, "w") as fh:
            fh.write(yaml.dump(config))


def main(args=None):
    TransformConfig().run(args)
