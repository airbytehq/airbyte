# DuckDB Migration Guide

## Upgrading to 0.5.0

This version updates the DuckDB libraries from `v0.10.3` to `v1.2.1`. Note that DuckDB `1.2.1` is backwards compatible with databases created using versions 0.10.x or higher of DuckDB. If your databases were created using an older version, you may need to manually upgrade your database file.

Note that forward compatibility is provided on a best effort basis, so upgrading may cause your databases to no longer be readable in prior versions of DuckDB. You can read more about the DuckDB storage format here: https://duckdb.org/docs/stable/internals/storage.html.

This breaking change will be enforced after May 7, 2025. Please plan to upgrade your databases before this date.

## Upgrading to 0.4.0

This version updates the DuckDB libraries from `v0.9.2` to `v0.10.3`. Note that DuckDB `0.10.x` is not backwards compatible with databases created in prior versions of DuckDB. You should upgrade your database file before upgrading this connector, and you should consider the impact on any other tooling you are using to connect to your database. Please see the [DuckDB 0.10.0 announcement](https://duckdb.org/2024/02/13/announcing-duckdb-0100.html) for more information and for upgrade instructions.

MotherDuck users will need to log into the MotherDuck UI at https://app.motherduck.com/, navigate to settings, and then opt in to the database conversion.

## Upgrading to 0.3.0

This version updates the DuckDB libraries from `v0.8.1` to `v0.9.1`. Note that DuckDB `0.9.x` is not backwards compatible with prior versions of DuckDB. Please see the [DuckDB 0.9.0 release notes](https://github.com/duckdb/duckdb/releases/tag/v0.9.0) for more information and for upgrade instructions.

MotherDuck users will need to log into the MotherDuck UI at https://app.motherduck.com/ and click "Start Upgrade". The upgrade prompt will automatically appear the next time the user logs in. If the prompt does not appear, then your database has been upgraded automatically, and in this case you are ready to use the latest version of the connector.
