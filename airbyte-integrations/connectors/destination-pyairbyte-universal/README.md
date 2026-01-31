# PyAirbyte Universal Destination

This is a universal destination connector that uses PyAirbyte's cache system to write data to various backends.

## Supported Backends

- **DuckDB**: Local or file-based DuckDB database
- **PostgreSQL**: PostgreSQL database
- **Snowflake**: Snowflake data warehouse
- **BigQuery**: Google BigQuery
- **MotherDuck**: MotherDuck cloud DuckDB

## Configuration

The connector accepts a `destination_type` parameter to select the backend, along with backend-specific configuration nested under the corresponding key.

### Example Configuration

```json
{
  "destination_type": "duckdb",
  "duckdb": {
    "db_path": "/local/my_database.duckdb",
    "schema_name": "main"
  }
}
```

## Development

For development and contribution guidelines, see the [Airbyte Connector Development Guide](https://docs.airbyte.com/connector-development/).
