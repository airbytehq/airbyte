#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

DEFAULT_SQL_TYPE = "jsonb"

AIRBYTE_TYPE_TO_SQL_TYPE = {
    "timestamp_with_timezone": "timestamp with time zone",
    "timestamp_without_timezone": "timestamp",
    "time_with_timezone": "time with time zone",
    "time_without_timezone": "time",
    "integer": "bigint",
    "big_integer": "bigint",
    "float": "decimal",
    "decimal": "decimal",
}

JSON_FORMAT_TO_SQL_TYPE = {
    "date": "date",
    "date-time": "timestamp with time zone",
}

JSON_TYPE_TO_SQL_TYPE = {
    "boolean": "boolean",
    "integer": "bigint",
    "number": "decimal",
    "string": "text",
    "array": DEFAULT_SQL_TYPE,
    "object": DEFAULT_SQL_TYPE,
}
