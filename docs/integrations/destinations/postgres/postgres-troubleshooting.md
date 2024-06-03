# Troubleshooting S3 Destinations

## Connector Limitations

### Postgres is not a Data Warehouse

:::danger

Postgres, while an excellent relational database, is not a data warehouse. Please only consider using postgres as a destination for small data volumes (e.g. less than 10GB) or for testing purposes. For larger data volumes, we recommend using a data warehouse like BigQuery, Snowflake, or Redshift.

:::

1. Postgres is likely to perform poorly with large data volumes. Even postgres-compatible
   destinations (e.g. AWS Aurora) are not immune to slowdowns when dealing with large writes or
   updates over ~100GB. Especially when using [typing and deduplication](/using-airbyte/core-concepts/typing-deduping) with `destination-postgres`, be sure to
   monitor your database's memory and CPU usage during your syncs. It is possible for your
   destination to 'lock up', and incur high usage costs with large sync volumes.
2. When attempting to scale a postgres database to handle larger data volumes, scaling IOPS (disk throughput) is as important as increasing memory and compute capacity.
3. Postgres column [name length limitations](https://www.postgresql.org/docs/current/limits.html)
   are likely to cause collisions when used as a destination receiving data from highly-nested and
   flattened sources, e.g. `{63 byte name}_a` and `{63 byte name}_b` will both be truncated to
   `{63 byte name}` which causes postgres to throw an error that a duplicate column name was
   specified. This limit is applicable to table names too.

### Vendor-Specific Connector Limitations

:::warning

Not all implementations or deployments of a database will be the same. This section lists specific limitations and known issues with the connector based on _how_ or _where_ it is deployed.

:::

#### Disk Access

The Airbyte Postgres destination relies on sending files to the database's temporary storage to then load in bulk. If your Postgres database does not have access to the `/tmp` file system, data loading will not succeed.
