#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from enum import Enum


class DestinationType(Enum):
    BIGQUERY = "bigquery"
    POSTGRES = "postgres"
    REDSHIFT = "redshift"
    SNOWFLAKE = "snowflake"
    MYSQL = "mysql"
    ORACLE = "oracle"

    @classmethod
    def from_string(cls, string_value: str) -> "DestinationType":
        return DestinationType[string_value.upper()]
