#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from enum import Enum


class DestinationType(Enum):
    BIGQUERY = "bigquery"
    MSSQL = "mssql"
    MYSQL = "mysql"
    ORACLE = "oracle"
    POSTGRES = "postgres"
    REDSHIFT = "redshift"
    SNOWFLAKE = "snowflake"
    CLICKHOUSE = "clickhouse"

    @classmethod
    def from_string(cls, string_value: str) -> "DestinationType":
        return DestinationType[string_value.upper()]
