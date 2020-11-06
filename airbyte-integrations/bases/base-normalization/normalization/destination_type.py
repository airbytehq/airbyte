from enum import Enum


class DestinationType(Enum):
    bigquery = "bigquery"
    postgres = "postgres"
    snowflake = "snowflake"
