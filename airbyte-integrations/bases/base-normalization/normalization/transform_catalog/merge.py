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

from normalization.transform_catalog.helper import jinja_call


class SchemaMerger:
    catalog: dict = {}

    def __init__(self, catalog: dict):
        self.catalog = catalog

    def generate_dbt_model(self, schema: str, json_col: str, normal_table_suffix: str, history_table_suffix: str) -> dict:
        result = {}
        for obj in self.catalog["streams"]:
            if "name" in obj:
                name = obj["name"]
            else:
                name = "undefined"
            # Incremental because same schema
            result[
                name
            ] = f"""{jinja_call(f"config(materialized='incremental')")}
with  {jinja_call(f"adapter.quote_as_configured('unioned', 'identifier')")} as (
{jinja_call(f"dbt_utils.union_relations([ref('{name}_history_in'), ref('{name}_normal')], exclude=['_dbt_source_relation'])")}
)
select distinct
    {jinja_call(f"dbt_utils.star(ref('{name}_history_in'), except=['_dbt_source_relation'])")}
from {jinja_call(f"adapter.quote_as_configured('unioned', 'identifier')")}
"""
        return result
