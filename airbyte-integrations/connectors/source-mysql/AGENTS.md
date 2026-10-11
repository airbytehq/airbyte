> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-mysql: Contributor notes

## Performance tests

Run performance tests from the repository root:

```bash
./gradlew :airbyte-integrations:connectors:source-mysql:performanceTest [--cpulimit=cpulimit/<limit>] [--memorylimit=memorylimit/<limit>]
```

In a pull request, trigger performance tests with:

```text
/test-performance connector=connectors/source-mysql [--cpulimit=cpulimit/<limit>] [--memorylimit=memorylimit/<limit>]
```

Parameters:

- `cpulimit`: maximum CPU count. The minimum is `2`, for example `--cpulimit=cpulimit/2`.
- `memorylimit`: maximum memory. Include a unit such as `MB` or `GB`. The minimum is `6MB`, for example `--memorylimit=memorylimit/4GB`.

If neither limit is provided, the performance tests run without CPU or memory limits. Available resources are bound by `ResourceRequirements.java`.

## Benchmark database setup

Use `src/test-performance/sql/create_mysql_benchmarks.sql` to create a benchmark database.

1. Create a database.
2. Update the TODOs in `create_mysql_benchmarks.sql` to set the table count and the record count for each size.
3. Run the script:

   ```bash
   cd airbyte-integrations/connectors/source-mysql
   mysql -h hostname -u user database < src/test-performance/sql/create_mysql_benchmarks.sql
   ```

The script creates the configured number of tables with names from `test_0` through `test_<table count minus 1>`.

## Reproducing bugs locally

Use the generic
[`source-mysql-e2e-tests`](.agents/skills/source-mysql-e2e-tests/SKILL.md)
skill for standard local sweeps and the
[`source-mysql-e2e-cdc-tests`](.agents/skills/source-mysql-e2e-cdc-tests/SKILL.md)
skill for binlog CDC cases. Both delegate orchestration to
[`airbyte-integrations/db-harness-lib/`](../../db-harness-lib/); the CDC skill
reuses the generic backend, which is already binlog and GTID ready.

```bash
GENERIC=airbyte-integrations/connectors/source-mysql/.agents/skills/source-mysql-e2e-tests
CDC=airbyte-integrations/connectors/source-mysql/.agents/skills/source-mysql-e2e-cdc-tests

"$GENERIC/scripts/start-backend.sh"
"$CDC/cases/initial-load.sh"
"$CDC/cases/incremental-replay.sh"
```
