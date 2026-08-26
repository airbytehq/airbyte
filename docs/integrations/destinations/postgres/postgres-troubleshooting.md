# Troubleshooting Postgres Destinations

## Connector Limitations

### Postgres is not a Data Warehouse

:::danger

Postgres, while an excellent relational database, is not a data warehouse. Please only consider using postgres as a destination for small data volumes (e.g. less than 10GB) or for testing purposes. For larger data volumes, we recommend using a data warehouse like BigQuery, Snowflake, or Redshift.

:::

1. Postgres is likely to perform poorly with large data volumes. Even postgres-compatible
   destinations (e.g. AWS Aurora) are not immune to slowdowns when dealing with large writes or
   updates over ~100GB. Especially when using [typing and deduplication](/platform/using-airbyte/core-concepts/typing-deduping) with `destination-postgres`, be sure to
   monitor your database's memory and CPU usage during your syncs. It is possible for your
   destination to 'lock up', and incur high usage costs with large sync volumes.
2. When attempting to scale a postgres database to handle larger data volumes, scaling IOPS (disk throughput) is as important as increasing memory and compute capacity.
3. Postgres limits identifiers to 63 bytes, so highly nested and flattened sources produce table and
   column names that the connector has to shorten. It appends a hash of the original name when it
   shortens one, so two long names that share a prefix don't collide, but the names in your
   destination won't match the ones in your source. See
   [Naming limitations](/integrations/destinations/postgres#naming-limitations) for the exact rules.

### Vendor-Specific Connector Limitations

:::warning

Not all implementations or deployments of a database will be the same. This section lists specific limitations and known issues with the connector based on _how_ or _where_ it is deployed.

:::

#### Disk Access

The connector batches records into a temporary CSV file and loads it with `COPY ... FROM STDIN`. The
file lives on the machine running the connector, not on the database server, so the destination
database needs no filesystem access. If the connector's own temporary directory is full or
read-only, syncs fail while writing the batch.
