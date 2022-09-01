#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from enum import Enum


class DestinationType(Enum):
    BIGQUERY = "bigquery"
    CLICKHOUSE = "clickhouse"
    MSSQL = "mssql"
    MYSQL = "mysql"
    ORACLE = "oracle"
    POSTGRES = "postgres"
    REDSHIFT = "redshift"
    SNOWFLAKE = "snowflake"
    TIDB = "tidb"

    @classmethod
    def from_string(cls, string_value: str) -> "DestinationType":
        return DestinationType[string_value.upper()]
