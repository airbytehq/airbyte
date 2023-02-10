#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from source_google_ads.utils import ParseGAQL


def test_parse_GAQL_ok():
    sql = ParseGAQL("SELECT field FROM table")
    assert sql.FieldNames == ["field"]
    assert sql.ResourceName == "table"
    assert sql.WhereClause is None
    assert sql.OrderByClause is None
    assert sql.LimitClause is None
    assert sql.ParametersClause is None
    assert sql.get_query() == "SELECT field FROM table"

    sql = ParseGAQL("SELECT field1, field2 FROM x_Table ")
    assert sql.FieldNames == ["field1", "field2"]
    assert sql.ResourceName == "x_Table"
    assert sql.WhereClause is None
    assert sql.OrderByClause is None
    assert sql.LimitClause is None
    assert sql.ParametersClause is None
    assert sql.get_query() == "SELECT field1, field2 FROM x_Table"

    sql = ParseGAQL("SELECT field1, field2 FROM x_Table WHERE date = '2020-01-01' ")
    assert sql.FieldNames == ["field1", "field2"]
    assert sql.ResourceName == "x_Table"
    assert sql.WhereClause == "date = '2020-01-01'"
    assert sql.OrderByClause is None
    assert sql.LimitClause is None
    assert sql.ParametersClause is None
    assert sql.get_query() == "SELECT field1, field2 FROM x_Table WHERE date = '2020-01-01'"

    sql = ParseGAQL("SELECT field1, field2 FROM x_Table WHERE date = '2020-01-01' ORDER  BY field2, field1 ")
    assert sql.FieldNames == ["field1", "field2"]
    assert sql.ResourceName == "x_Table"
    assert sql.WhereClause == "date = '2020-01-01'"
    assert sql.OrderByClause == "field2, field1"
    assert sql.LimitClause is None
    assert sql.ParametersClause is None
    assert sql.get_query() == "SELECT field1, field2 FROM x_Table WHERE date = '2020-01-01' ORDER BY field2, field1"

    sql = ParseGAQL("SELECT t.field1, t.field2 FROM x_Table ORDER  BY field2, field1 LIMIT 10 ")
    assert sql.FieldNames == ["t.field1", "t.field2"]
    assert sql.ResourceName == "x_Table"
    assert sql.WhereClause is None
    assert sql.OrderByClause == "field2, field1"
    assert sql.LimitClause == 10
    assert sql.ParametersClause is None
    assert sql.get_query() == "SELECT t.field1, t.field2 FROM x_Table ORDER BY field2, field1 LIMIT 10"

    sql = ParseGAQL("""
        SELECT field1, field2
          FROM x_Table
         WHERE date = '2020-01-01'
      ORDER BY field2 ASC, field1 DESC
         LIMIT 10
    PARAMETERS include_drafts=true """)

    assert sql.FieldNames == ["field1", "field2"]
    assert sql.ResourceName == "x_Table"
    assert sql.WhereClause == "date = '2020-01-01'"
    assert sql.OrderByClause == "field2 ASC, field1 DESC"
    assert sql.LimitClause == 10
    assert sql.ParametersClause == "include_drafts=true"
    assert sql.get_query() == "SELECT field1, field2 FROM x_Table WHERE date = '2020-01-01' ORDER BY field2 ASC, field1 DESC LIMIT 10 PARAMETERS include_drafts=true"


def test_parse_GAQL_fail():
    with pytest.raises(Exception) as e:
        ParseGAQL("SELECT field1, field2 FROM x_Table2")
    assert str(e.value) == "incorrect GAQL query statement: 'SELECT field1, field2 FROM x_Table2'"

    with pytest.raises(Exception) as e:
        ParseGAQL("SELECT field1, field2 FROM x_Table WHERE ")
