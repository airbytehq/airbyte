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
import os

import yaml
from normalization.transform_catalog.comparable import ComparableModel
from normalization.transform_catalog.helper import jinja_call
from normalization.transform_catalog.history import HistoryLoader
from normalization.transform_catalog.merge import SchemaMerger
from normalization.transform_catalog.normalize import JsonSchemaNormalizer


class TransformCatalog:
    config: dict = {}

    def run(self, args) -> None:
        self.parse(args)
        self.process_catalog()

    def parse(self, args) -> None:
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument(
            "--profile-config-dir",
            type=str,
            required=True,
            help="path to directory containing DBT profiles.yml",
        )
        parser.add_argument(
            "--catalog",
            nargs="+",
            type=str,
            required=True,
            help="path to Catalog (JSON Schema) file",
        )
        parser.add_argument(
            "--out",
            type=str,
            required=True,
            help="path to output generated DBT Models to",
        )
        parser.add_argument(
            "--json-column",
            type=str,
            required=False,
            help="name of the column containing the json blob",
        )
        parser.add_argument(
            "--table-suffix",
            type=str,
            required=False,
            help="suffix to tables in catalog to find raw versions",
        )
        parsed_args = parser.parse_args(args)
        profiles_yml = read_profiles_yml(parsed_args.profile_config_dir)
        self.config = {
            "schema": extract_schema(profiles_yml),
            "catalog": parsed_args.catalog,
            "output_path": parsed_args.out,
            "json_column": parsed_args.json_column,
            "table_suffix": parsed_args.table_suffix,
        }

    def process_catalog(self) -> None:
        source_tables: set = set()
        schema = self.config["schema"]
        json_column = self.config["json_column"]
        if not json_column:
            json_column = "data"
        table_suffix = self.config["table_suffix"]
        if not table_suffix:
            table_suffix = "_raw"
        output = self.config["output_path"]
        for catalog_file in self.config["catalog"]:
            print(f"Processing {catalog_file}...")
            catalog = read_json_catalog(catalog_file)

            # Generate _comparable
            comparable = ComparableModel(catalog)
            result, tables = comparable.generate_dbt_model(schema=schema, json_col=json_column, table_suffix=table_suffix)
            source_tables = source_tables.union(tables)
            self.output_sql_models(os.path.join(output, "temporary"), result, "_comparable")

            # Generate _history_raw_out
            for table in result:
                result[table] = (
                    jinja_call("config(materialized='incremental')") + "\nselect * from " + jinja_call(f"ref('{table}_comparable')")
                )
            self.output_sql_models(output, result, "_history_raw_out")

            # Generate _normal
            normalizer = JsonSchemaNormalizer(catalog)
            result = normalizer.generate_dbt_model(
                schema=schema,
                json_col=json_column,
                table_suffix="_comparable",
            )
            self.output_sql_models(os.path.join(output, "temporary"), result, "_normal")

            # Generate _history_in
            history = HistoryLoader(catalog)
            result, tables = history.generate_dbt_model(
                schema=schema,
                json_col=json_column,
                normal_table_suffix="_normal",
                history_table_suffix="_history_out",
            )
            source_tables = source_tables.union(tables)
            self.output_sql_models(os.path.join(output, "temporary"), result, "_history_in")

            # Generate merged table _history_out
            merger = SchemaMerger(catalog)
            result = merger.generate_dbt_model(
                schema=schema,
                json_col=json_column,
                normal_table_suffix="_normal",
                history_table_suffix="_history_in",
            )
            self.output_sql_models(output, result, "_history_out")

            # TODO Generate _latest_out

        self.write_yaml_sources(output, schema, source_tables)

    @staticmethod
    def output_sql_models(output: str, result: dict, table_suffix: str = "") -> None:
        if result:
            if not os.path.exists(output):
                os.makedirs(output)
            for file, sql in result.items():
                print(f"  Generating {file}{table_suffix}.sql in {output}")
                with open(os.path.join(output, f"{file}{table_suffix}.sql"), "w") as f:
                    f.write(sql)

    @staticmethod
    def write_yaml_sources(output: str, schema: str, sources: set) -> None:
        tables = [{"name": source} for source in sources]
        source_config = {
            "version": 2,
            "sources": [
                {
                    "name": schema,
                    "tables": tables,
                    "quoting": {
                        "database": True,
                        "schema": True,
                        "identifier": True,
                    },
                },
            ],
        }
        # Quoting options are hardcoded and passed down to the sources instead of
        # inheriting them from dbt_project.yml (does not work well for some reasons?)
        # Apparently, Snowflake needs this quoting configuration to work properly...
        source_path = os.path.join(output, "sources.yml")
        if not os.path.exists(source_path):
            with open(source_path, "w") as fh:
                fh.write(yaml.dump(source_config))


def read_profiles_yml(profile_dir: str) -> dict:
    with open(os.path.join(profile_dir, "profiles.yml"), "r") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
        obj = config["normalize"]["outputs"]["prod"]
        return obj


def extract_schema(profiles_yml: dict) -> str:
    if "dataset" in profiles_yml:
        return profiles_yml["dataset"]
    else:
        return profiles_yml["schema"]


def read_json_catalog(input_path: str) -> dict:
    with open(input_path, "r") as file:
        contents = file.read()
    return json.loads(contents)


def main(args=None):
    TransformCatalog().run(args)
