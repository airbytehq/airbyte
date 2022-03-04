# ClickHouse

## Overview

ClickHouse is a fast open-source column-oriented database management system that allows generating analytical data reports in real-time using SQL queries.

## Endpoints

This destination connector uses ClickHouse official JDBC driver, which uses HTTP as protocol. [https://github.com/ClickHouse/clickhouse-jdbc](https://github.com/ClickHouse/clickhouse-jdbc)

## Quick Notes

- ClickHouse JDBC driver uses HTTP protocal (default 8123) but [dbt clickhouse adapter](https://github.com/silentsokolov/dbt-clickhouse) use TCP protocal (default 9000).

- This connector doesn't support nested streams and schema change yet.

- The community [dbt clickhouse adapter](https://github.com/silentsokolov/dbt-clickhouse) has some bugs haven't been fixed yet, for example [https://github.com/silentsokolov/dbt-clickhouse/issues/20](https://github.com/silentsokolov/dbt-clickhouse/issues/20), so the dbt test is based on a fork [https://github.com/burmecia/dbt-clickhouse](https://github.com/burmecia/dbt-clickhouse).

## API Reference

The ClickHouse reference documents: [https://clickhouse.com/docs/en/](https://clickhouse.com/docs/en/)

