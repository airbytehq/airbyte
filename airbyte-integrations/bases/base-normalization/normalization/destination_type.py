#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
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
    DUCKDB = "duckdb"

    @classmethod
    def from_string(cls, string_value: str) -> "DestinationType":
        return DestinationType[string_value.upper()]

    @staticmethod
    def testable_destinations():
        return [dest for dest in list(DestinationType) if dest != DestinationType.DUCKDB]
