# MongoDB V2 Destination

MongoDB destination connector built with the Dataflow CDK (Bulk CDK).

## Features

### **Sync Modes**
- ✅ **Append** - Insert new records (bulk insertMany)
- ✅ **Overwrite** - Full refresh with atomic collection swap
- ✅ **Append+Dedup** - Incremental with primary key deduplication

### **Advanced Features**
- ✅ **Incremental Sync** - Track changes with cursor fields
- ✅ **Primary Key Support** - Unique indexes + deduplication
- ✅ **Generation ID Tracking** - Handles sync generations
- ✅ **CDC Soft Delete** - Preserves deletion timestamps
- ✅ **Schema Evolution** - Automatic (schemaless database)
- ✅ **Batch Insert** - Optimized bulk write operations (10,000 records/batch default)
- ✅ **Native Upsert** - MongoDB $merge aggregation pipeline

### **Performance**
- **Batch Size**: Configurable (1-100,000 records)
- **Insert Method**: insertMany() bulk operation
- **Upsert Method**: Aggregation pipeline with $merge (server-side)
- **Typical Throughput**: 5,000-50,000 records/sec (depending on document size and network)

## Configuration

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `connection_string` | string | Yes | - | MongoDB connection string |
| `database` | string | Yes | `airbyte` | Target database name |
| `auth_source` | string | No | `admin` | Authentication database |
| `batch_size` | integer | No | `10,000` | Records per batch (1-100,000) |

### Connection String Format

```
mongodb://[username:password@]host[:port]/[database][?options]
```

**Examples:**
- **Standard**: `mongodb://user:pass@localhost:27017/mydb`
- **Replica Set**: `mongodb://host1:27017,host2:27017/mydb?replicaSet=rs0`
- **MongoDB Atlas**: `mongodb+srv://user:pass@cluster.mongodb.net/mydb`
- **From Kubernetes**: `mongodb://user:pass@host.docker.internal:27017/mydb` (Mac/Windows)

### Authentication

Supports all MongoDB authentication mechanisms:
- SCRAM-SHA-1 / SCRAM-SHA-256 (default)
- MONGODB-X509
- GSSAPI (Kerberos)
- PLAIN

Specify via connection string options: `?authMechanism=SCRAM-SHA-256`

## How It Works

### **Append Mode**
1. Creates collection if not exists
2. Batches records in memory (up to batch_size)
3. Flushes via insertMany() bulk operation
4. No deduplication

### **Overwrite Mode**
1. Writes all data to temporary collection
2. Atomically renames temp → final collection
3. Drops old collection
4. Ensures consistency during refresh

### **Dedupe Mode**
1. Writes all records to temporary collection
2. Runs aggregation pipeline:
   - Groups by primary key
   - Sorts by cursor field (keeps latest)
   - Merges into final collection
3. Leverages MongoDB's $merge operator for atomic upsert

### **CDC Support**
- Soft delete records include `_ab_cdc_deleted_at` timestamp
- Records are upserted with deletion metadata
- Downstream consumers filter by checking if field exists
- Hard delete mode: Not recommended for MongoDB (would require post-merge cleanup)

## Type Mapping

| Airbyte Type | MongoDB BSON Type | Notes |
|--------------|-------------------|-------|
| STRING | String | - |
| INTEGER | Long | 64-bit integer |
| NUMBER | Double | IEEE 754 double |
| BOOLEAN | Boolean | - |
| DATE | String | ISO 8601 format |
| TIMESTAMP_WITH_TZ | Long | Milliseconds since epoch |
| TIMESTAMP_WITHOUT_TZ | String | ISO 8601 format |
| TIME | String | ISO 8601 format |
| OBJECT | Document | Nested document |
| ARRAY | Array | Nested array |
| NULL | null | - |

## Development

Built using the Airbyte Dataflow CDK (Bulk CDK) - local development version.

### Build
```bash
./gradlew :airbyte-integrations:connectors:destination-mongodb-v2:build
```

### Test
```bash
# Component tests (uses Testcontainers)
./gradlew :airbyte-integrations:connectors:destination-mongodb-v2:integrationTestNonDocker --tests "Mongodb*Test"

# All integration tests
./gradlew :airbyte-integrations:connectors:destination-mongodb-v2:integrationTest
```

### Docker Build
```bash
./gradlew :airbyte-integrations:connectors:destination-mongodb-v2:assemble
```

## Architecture

### **Components**
- **MongodbClient** - Database operations (TableOperationsClient)
- **MongodbWriter** - Write orchestration (creates StreamLoaders)
- **MongodbAggregate** - Record batching
- **MongodbInsertBuffer** - Bulk insert with insertMany()
- **MongodbChecker** - Connection validation

### **Upsert Strategy**
Uses MongoDB aggregation pipeline:
```javascript
[
  { $sort: { cursor: -1, _airbyte_extracted_at: -1 } },
  { $group: { _id: "$pk", doc: { $first: "$$ROOT" } } },
  { $replaceRoot: { newRoot: "$doc" } },
  { $merge: { into: "target", on: ["pk"], whenMatched: "replace", whenNotMatched: "insert" } }
]
```

### **Primary Keys**
- Creates unique compound index on primary key fields
- Used for deduplication during upsert operations
- Prevents duplicate records

## Limitations

- **Nested Primary Keys**: Not supported (only top-level fields)
- **Nested Cursors**: Not supported (only top-level fields)
- **Hard Delete CDC**: Soft delete only (deletion timestamp preserved in document)

## Troubleshooting

### Connection Issues
- **Authentication failed**: Check connection_string username/password
- **Server not found**: Verify host is accessible from connector
- **SSL/TLS errors**: Add `?tls=true` to connection string if required

### Performance
- **Slow inserts**: Increase batch_size (try 50,000-100,000)
- **Out of memory**: Decrease batch_size or tune AggregatePublishingConfig
- **Network timeouts**: Reduce batch_size for slow networks

### From Kubernetes
Use `host.docker.internal` (Mac/Windows) or actual host IP (Linux):
```
mongodb://user:pass@host.docker.internal:27017/mydb
```
