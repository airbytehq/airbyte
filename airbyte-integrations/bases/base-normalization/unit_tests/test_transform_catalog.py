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

        # unless quoted, redshift and postgres coerce table names to lower case.
        assert normalize_identifier_name(identifier_name, "redshift") == "approved_users"
        assert normalize_identifier_name(identifier_name, "postgres") == "approved_users"
        assert normalize_identifier_name(identifier_name, "bigquery") == "Approved_Users"
        assert normalize_identifier_name(identifier_name, "snowflake") == "Approved_Users"

    def test_table_name(self):
        tableName1 = "Approved@Users"

        assert table_name(tableName1, "redshift") == '"Approved@Users"'
        assert table_name(tableName1, "postgres") == '"Approved@Users"'
        assert table_name(tableName1, "bigquery") == "Approved_Users"
        assert table_name(tableName1, "snowflake") == '"Approved@Users"'

        tableName2 = "ApprovedUsers"

        # unless quoted, redshift and postgres coerce table names to lower case.
        assert table_name(tableName2, "redshift") == "approvedusers"
        assert table_name(tableName2, "postgres") == "approvedusers"
        assert table_name(tableName2, "bigquery") == "ApprovedUsers"
        assert table_name(tableName2, "snowflake") == "ApprovedUsers"
