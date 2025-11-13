# MongoDB V2 Destination

Modern MongoDB destination connector built on Airbyte's Dataflow CDK.

## Features

- **All Sync Modes**: Append, Dedupe (incremental), Full Refresh with Overwrite
- **Efficient Batching**: Configurable batch sizes with MongoDB's `insertMany`
- **Native MongoDB Operations**: Uses aggregation pipeline for deduplication
- **Schema-less**: Leverages MongoDB's flexible document model
- **Connection Pooling**: Built-in connection pool management
- **Error Handling**: Comprehensive error classification and retry logic

## Configuration

```json
{
  "connection_string": "mongodb://localhost:27017",
  "database": "my_database",
  "auth_type": "login/password",
  "username": "user",
  "password": "password",
  "batch_size": 1000
}
```

### Configuration Parameters

- `connection_string` (required): MongoDB connection string (supports `mongodb://` and `mongodb+srv://`)
- `database` (required): Target database name
- `auth_type` (optional): Authentication type (`login/password` or `none`)
- `username` (optional): Username for authentication
- `password` (optional): Password for authentication
- `batch_size` (optional): Number of documents to buffer before flushing (default: 1000)

## Implementation Details

### Architecture

This connector follows the Dataflow CDK pattern with NoSQL-specific adaptations:

1. **MongodbAirbyteClient**: Implements `TableOperationsClient` and `TableSchemaEvolutionClient`
   - Collections treated as "tables"
   - Indexes created for primary keys and cursors
   - Schema evolution is no-op (MongoDB is schemaless)

2. **MongodbInsertBuffer**: Batch writer using `insertMany`
   - Configurable batch size
   - Automatic type conversion (AirbyteValue → BSON)
   - Native support for dates, arrays, and nested documents

3. **Deduplication Strategy**: Uses MongoDB aggregation pipeline
   ```javascript
   [
     { $sort: { cursor: -1 } },
     { $group: { _id: primaryKey, doc: { $first: "$$ROOT" } } },
     { $replaceRoot: { newRoot: "$doc" } }
   ]
   ```
   This is the NoSQL equivalent of SQL window functions.

4. **StreamLoaders**: Uses all 4 CDK-provided loaders
   - `DirectLoadTableAppendStreamLoader`: Incremental append
   - `DirectLoadTableDedupStreamLoader`: Incremental with deduplication
   - `DirectLoadTableAppendTruncateStreamLoader`: Full refresh append
   - `DirectLoadTableDedupTruncateStreamLoader`: Full refresh with deduplication

### NoSQL Adaptations

| SQL Operation | MongoDB Equivalent |
|---------------|-------------------|
| `CREATE SCHEMA` | Implicit (created on first collection) |
| `CREATE TABLE` | `db.createCollection()` + create indexes |
| `DROP TABLE` | `collection.drop()` |
| `INSERT` | `collection.insertMany()` |
| `MERGE INTO` | Aggregation pipeline + `replaceOne(upsert=true)` |
| `ALTER TABLE ADD COLUMN` | No-op (schemaless) |
| `SWAP tables` | `collection.renameCollection()` |

### Key Differences from V1

- **Modern CDK**: Uses Dataflow CDK instead of deprecated CDK
- **Better Performance**: Batch operations with `insertMany`
- **True Deduplication**: Uses aggregation pipeline instead of hash-based dedup
- **All Sync Modes**: Full support for append, dedupe, and overwrite
- **Better Error Handling**: Proper error classification (ConfigError, TransientError, SystemError)
- **Connection Pooling**: Built-in connection pool management

## Development

### Build

```bash
./gradlew :airbyte-integrations:connectors:destination-mongodb-v2:build
```

### Test

```bash
./gradlew :airbyte-integrations:connectors:destination-mongodb-v2:test
```

### Run

```bash
./gradlew :airbyte-integrations:connectors:destination-mongodb-v2:run --args='write'
```

## Testing

Uses Testcontainers for integration testing with real MongoDB instance.

## Performance Considerations

- **Batch Size**: Adjust based on document size and available memory
- **Indexes**: Automatically created on PK fields and `_airbyte_extracted_at`
- **Deduplication**: Aggregation pipeline is efficient but may use memory for large datasets
- **Connection Pool**: Configured for up to 20 concurrent connections

## Limitations

- Deduplication aggregation may be memory-intensive for very large datasets
- No support for transactions (uses `insertMany` with `ordered=false`)
- Collection names limited to 120 characters

## License

MIT
