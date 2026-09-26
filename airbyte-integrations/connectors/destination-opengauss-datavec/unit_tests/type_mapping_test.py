#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import pytest
from destination_opengauss_datavec.schema import schema_to_sql_type
from destination_opengauss_datavec.type_mapping import AIRBYTE_TYPE_TO_SQL_TYPE, JSON_FORMAT_TO_SQL_TYPE, JSON_TYPE_TO_SQL_TYPE


@pytest.mark.parametrize("airbyte_type,sql_type", AIRBYTE_TYPE_TO_SQL_TYPE.items())
def test_airbyte_types_map_to_sql_types(airbyte_type, sql_type):
    assert schema_to_sql_type({"type": "string", "airbyte_type": airbyte_type}) == sql_type


@pytest.mark.parametrize("json_format,sql_type", JSON_FORMAT_TO_SQL_TYPE.items())
def test_json_formats_map_to_sql_types(json_format, sql_type):
    assert schema_to_sql_type({"type": "string", "format": json_format}) == sql_type


@pytest.mark.parametrize("json_type,sql_type", JSON_TYPE_TO_SQL_TYPE.items())
def test_json_types_map_to_sql_types(json_type, sql_type):
    assert schema_to_sql_type({"type": json_type}) == sql_type


def test_airbyte_type_takes_precedence_over_json_format_and_type():
    assert schema_to_sql_type({"type": "integer", "format": "date-time", "airbyte_type": "time_without_timezone"}) == "time"


def test_nullable_single_json_type_uses_non_null_type():
    assert schema_to_sql_type({"type": ["null", "integer"]}) == "bigint"


def test_multiple_json_types_fall_back_to_jsonb():
    assert schema_to_sql_type({"type": ["string", "integer"]}) == "jsonb"
