#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import argparse
import os
from typing import Any, Dict

import yaml
from normalization.destination_type import DestinationType
from normalization.transform_catalog.catalog_processor import CatalogProcessor


class TransformCatalog:
    """
To run this transformation:
```
python3 main_dev_transform_catalog.py \
  --integration-type <postgres|bigquery|redshift|snowflake>
  --profile-config-dir . \
  --catalog integration_tests/catalog.json \
  --out dir \
  --json-column json_blob
```
    """

    config: dict = {}

    def __init__(self):
        self.config = {}

    def run(self, args) -> None:
        self.parse(args)
        self.process_catalog()

    def parse(self, args) -> None:
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--integration-type", type=str, required=True, help="type of integration dialect to use")
        parser.add_argument("--profile-config-dir", type=str, required=True, help="path to directory containing DBT profiles.yml")
        parser.add_argument("--catalog", nargs="+", type=str, required=True, help="path to Catalog (JSON Schema) file")
        parser.add_argument("--out", type=str, required=True, help="path to output generated DBT Models to")
        parser.add_argument("--json-column", type=str, required=False, help="name of the column containing the json blob")
        parsed_args = parser.parse_args(args)
        profiles_yml = read_profiles_yml(parsed_args.profile_config_dir)
        self.config = {
            "integration_type": parsed_args.integration_type,
            "schema": extract_schema(profiles_yml),
            "catalog": parsed_args.catalog,
            "output_path": parsed_args.out,
            "json_column": parsed_args.json_column,
        }

    def process_catalog(self) -> None:
        destination_type = DestinationType.from_string(self.config["integration_type"])
        schema = self.config["schema"]
        output = self.config["output_path"]
        json_col = self.config["json_column"]
        processor = CatalogProcessor(output_directory=output, destination_type=destination_type)
        for catalog_file in self.config["catalog"]:
            print(f"Processing {catalog_file}...")
            processor.process(catalog_file=catalog_file, json_column_name=json_col, default_schema=schema)


def read_profiles_yml(profile_dir: str) -> Any:
    with open(os.path.join(profile_dir, "profiles.yml"), "r") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
        obj = config["normalize"]["outputs"]["prod"]
        return obj


def extract_schema(profiles_yml: Dict) -> str:
    if "dataset" in profiles_yml:
        return str(profiles_yml["dataset"])
    elif "schema" in profiles_yml:
        return str(profiles_yml["schema"])
    else:
        raise KeyError("No Dataset/Schema defined in profiles.yml")


def main(args=None):
    TransformCatalog().run(args)
