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
from pkg_resources import resource_string


class HistoryLoader:
    catalog: dict = {}

    def __init__(self, catalog: dict):
        self.catalog = catalog

    def generate_dbt_model(self, schema: str, json_col: str, normal_table_suffix: str, history_table_suffix: str):
        result = {}
        source_tables = set()
        for obj in self.catalog["streams"]:
            if "name" in obj:
                name = obj["name"]
            else:
                name = "undefined"
            template = resource_string("normalization.resources", "history_template.sql")
            tmp = template.decode("UTF-8")
            tmp = tmp.replace("{schema}", schema)
            tmp = tmp.replace("{name}", f"{name}{history_table_suffix}")
            tmp = tmp.replace("{alternative}", f"{name}{normal_table_suffix}")
            result[name] = tmp
            source_tables.add(f"{name}{history_table_suffix}")
        return result, source_tables
