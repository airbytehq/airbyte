# Postgres Source

## Performance Test

To run performance tests in commandline:
```shell
./gradlew :airbyte-integrations:connectors:source-postgres:performanceTest [--cpulimit=cpulimit/<limit>] [--memorylimit=memorylimit/<limit>]
```

In pull request:
```shell
/test-performance connector=connectors/source-postgres [--cpulimit=cpulimit/<limit>] [--memorylimit=memorylimit/<limit>]
```

- `cpulimit`: Limit the number of CPUs. The minimum is `2`. E.g. `--cpulimit=cpulimit/2`.
- `memorylimit`: Limit the size of the memory. Must include the unit at the end (e.g. `MB`, `GB`). The minimum size is `6MB`. E.g. `--memorylimit=memorylimit/4GB`.
- When none of the CPU or memory limit is provided, the performance tests will run without memory or CPU limitations. The available resource will be bound that those specified in `ResourceRequirements.java`.

### Use Postgres script to populate the benchmark database

In order to create a database with a certain number of tables, and a certain number of records in each of them, 
you need to follow a few simple steps.

1. Create a new database.
2. Follow the TODOs in [3-run-script.sql](src/test-performance/sql/3-run-script.sql) to change the number of tables, and the number of records of different sizes.
3. On the new database, run the following script:
   ```shell
   cd airbyte-integrations/connectors/source-postgres
   psql -h <host> -d <db-name> -U <username> -p <port> -a -q -f src/test-performance/sql/1-create-copy-tables-procedure.sql
   psql -h <host> -d <db-name> -U <username> -p <port> -a -q -f src/test-performance/sql/2-create-insert-rows-to-table-procedure.sql
   psql -h <host> -d <db-name> -U <username> -p <port> -a -q -f src/test-performance/sql/3-run-script.sql
   ```
4. After the script finishes, you will receive the number of tables specified in the script, with names starting with **test_0** and ending with **test_(the number of tables minus 1)**.
