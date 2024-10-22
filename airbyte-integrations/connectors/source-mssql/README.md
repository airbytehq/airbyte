# MsSQL (SQL Server) Source

## Performance Test

To run performance tests in commandline:

```shell
./gradlew :airbyte-integrations:connectors:source-mssql:performanceTest [--cpulimit=cpulimit/<limit>] [--memorylimit=memorylimit/<limit>]
```

In pull request:

```shell
/test-performance connector=connectors/source-mssql [--cpulimit=cpulimit/<limit>] [--memorylimit=memorylimit/<limit>]
```

- `cpulimit`: Limit the number of CPUs. The minimum is `2`. E.g. `--cpulimit=cpulimit/2`.
- `memorylimit`: Limit the size of the memory. Must include the unit at the end (e.g. `MB`, `GB`). The minimum size is `6MB`. E.g. `--memorylimit=memorylimit/4GB`.
- When none of the CPU or memory limit is provided, the performance tests will run without memory or CPU limitations. The available resource will be bound that those specified in `ResourceRequirements.java`.

### Use MsSQL script to populate the benchmark database

In order to create a database with a certain number of tables, and a certain number of records in each of them,
you need to follow a few simple steps.

1. Create a new database.
2. Follow the TODOs in [create_mssql_benchmarks.sql](src/test-performance/sql/create_mssql_benchmarks.sql) to change the number of tables, and the number of records of different sizes.
3. Execute the script with your changes for the new database. You can run the script with the MySQL client:
   ```bash
   cd airbyte-integrations/connectors/source-mssql
   sqlcmd -S Serverinstance -E -i src/test-performance/sql/create_mssql_benchmarks.sql
   ```
4. After the script finishes its work, you will receive the number of tables specified in the script, with names starting with **test_0** and ending with **test\_(the number of tables minus 1)**.
