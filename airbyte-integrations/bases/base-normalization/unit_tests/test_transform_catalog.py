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

from normalization.transform_catalog.transform import normalize_identifier_name, table_name


class TestTransformCatalog:
    def test_normalize_identifier_name(self):
        identifier_name = "Approved@Users"

        # redshift and postgres coerce identifier names to lower case. dbt
        # redshift cannot access identifiers if they are not properly cased.
        assert normalize_identifier_name(identifier_name, "redshift") == "approved_users"
        assert normalize_identifier_name(identifier_name, "postgres") == "Approved_Users"
        assert normalize_identifier_name(identifier_name, "bigquery") == "Approved_Users"
        assert normalize_identifier_name(identifier_name, "snowflake") == "Approved_Users"

    def test_table_name(self):
        table_name1 = "Approved@Users"

        # redshift coerces even quoted names to lower case.
        assert table_name(table_name1, "redshift") == '"approved@users"'
        assert table_name(table_name1, "postgres") == '"Approved@Users"'
        assert table_name(table_name1, "bigquery") == "Approved_Users"
        assert table_name(table_name1, "snowflake") == '"Approved@Users"'

        table_name2 = "ApprovedUsers"

        # redshift and postgres coerce non-quoted table names to lower case.
        # normalization fails on second attempt if these names are not lower
        # cased because DBT finds an "approximate" match.
        # (issue: https://github.com/airbytehq/airbyte/issues/1926)
        assert table_name(table_name2, "redshift") == "approvedusers"
        assert table_name(table_name2, "postgres") == "approvedusers"
        assert table_name(table_name2, "bigquery") == "ApprovedUsers"
        assert table_name(table_name2, "snowflake") == "ApprovedUsers"
