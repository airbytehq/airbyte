---
products: embedded
---

# Schema Discovery

Schema discovery allows you to programmatically explore the data structure of your customers' connected sources. This is useful for building dynamic UIs, validating data schemas, and understanding what data is available from each source.

## Overview

Once a customer has configured a source, you can discover:
- **Streams**: The tables/collections/endpoints available in the source
- **Fields**: The columns/properties within each stream
- **Data Types**: The type of each field (string, number, date, etc.)
- **Primary Keys**: Which fields uniquely identify records
- **Relationships**: How streams relate to each other (for some sources)

## Discovery Process

### 1. Trigger Discovery

Discovery is the process of connecting to the source and retrieving its schema metadata. This happens automatically when:
- A source is first configured
- A source is updated
- Manual refresh is triggered

To manually trigger discovery:

```bash
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/sources/{source_id}/discover' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -H 'Content-Type: application/json'
```

**Response:**
```json
{
  "job_id": "discover_12345",
  "status": "running"
}
```

### 2. Query the Catalog

Once discovery is complete, query the full catalog:

```bash
curl -X GET 'https://api.airbyte.ai/api/v1/integrations/sources/{source_id}/catalog/query' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

**Response:**
```json
{
  "streams": [
    {
      "name": "customers",
      "json_schema": {
        "type": "object",
        "properties": {
          "id": {
            "type": "string"
          },
          "email": {
            "type": "string",
            "format": "email"
          },
          "created_at": {
            "type": "string",
            "format": "date-time"
          },
          "metadata": {
            "type": "object"
          }
        }
      },
      "supported_sync_modes": ["full_refresh", "incremental"],
      "source_defined_cursor": true,
      "default_cursor_field": ["created_at"],
      "source_defined_primary_key": [["id"]],
      "namespace": "public"
    },
    {
      "name": "orders",
      "json_schema": {
        "type": "object",
        "properties": {
          "id": {
            "type": "string"
          },
          "customer_id": {
            "type": "string"
          },
          "amount": {
            "type": "number"
          },
          "status": {
            "type": "string",
            "enum": ["pending", "completed", "cancelled"]
          },
          "created_at": {
            "type": "string",
            "format": "date-time"
          }
        }
      },
      "supported_sync_modes": ["full_refresh", "incremental"],
      "source_defined_cursor": true,
      "default_cursor_field": ["created_at"],
      "source_defined_primary_key": [["id"]]
    }
  ]
}
```

## Stream Information

### Available Streams

Get a list of all streams without detailed schema:

```bash
curl -X GET 'https://api.airbyte.ai/api/v1/integrations/sources/{source_id}/streams' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

**Response:**
```json
{
  "streams": [
    {
      "name": "customers",
      "namespace": "public"
    },
    {
      "name": "orders",
      "namespace": "public"
    },
    {
      "name": "products",
      "namespace": "public"
    }
  ]
}
```

### Single Stream Details

Get detailed information about a specific stream:

```bash
curl -X GET 'https://api.airbyte.ai/api/v1/integrations/sources/{source_id}/streams/customers' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

**Response:**
```json
{
  "name": "customers",
  "namespace": "public",
  "json_schema": {
    "type": "object",
    "properties": {
      "id": { "type": "string" },
      "email": { "type": "string" },
      "created_at": { "type": "string", "format": "date-time" }
    }
  },
  "supported_sync_modes": ["full_refresh", "incremental"],
  "source_defined_cursor": true,
  "default_cursor_field": ["created_at"],
  "source_defined_primary_key": [["id"]]
}
```

## Understanding Schema Structure

### JSON Schema Format

Airbyte uses [JSON Schema](https://json-schema.org/) to describe data types:

| JSON Schema Type | Description | Example Values |
|-----------------|-------------|----------------|
| `string` | Text data | `"hello"`, `"user@example.com"` |
| `number` | Numeric data (int or float) | `42`, `3.14` |
| `integer` | Whole numbers only | `42`, `-7` |
| `boolean` | True/false values | `true`, `false` |
| `object` | Nested JSON objects | `{"key": "value"}` |
| `array` | Lists of values | `[1, 2, 3]` |
| `null` | Null/empty values | `null` |

### Format Specifiers

Some fields have additional format information:

| Format | Description | Example |
|--------|-------------|---------|
| `date-time` | ISO 8601 timestamp | `"2024-10-09T19:00:00Z"` |
| `date` | Date only | `"2024-10-09"` |
| `time` | Time only | `"19:00:00"` |
| `email` | Email address | `"user@example.com"` |
| `uri` | URL/URI | `"https://example.com"` |
| `uuid` | UUID identifier | `"550e8400-e29b-41d4-a716-446655440000"` |

### Sync Modes

Each stream supports different sync modes:

**Full Refresh:**
- Downloads all records every sync
- Replaces previous data
- Use for small datasets or when you need complete snapshots

**Incremental:**
- Downloads only new/changed records
- Uses a cursor field (typically timestamp)
- More efficient for large datasets

### Primary Keys

Primary keys uniquely identify records and enable:
- Deduplication
- Upsert operations
- Change data capture (CDC)

Primary keys are represented as an array of arrays:
```json
"source_defined_primary_key": [["id"]]  // Single column key
"source_defined_primary_key": [["tenant_id"], ["user_id"]]  // Composite key
```

## Use Cases

### Building Dynamic UI

Use schema discovery to build adaptive UIs that change based on available data:

```javascript
async function buildDataExplorer(sourceId, token) {
  // Get available streams
  const streamsResponse = await fetch(
    `https://api.airbyte.ai/api/v1/integrations/sources/${sourceId}/streams`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  const { streams } = await streamsResponse.json();

  // Let user select a stream
  const selectedStream = await showStreamSelector(streams);

  // Get detailed schema for selected stream
  const schemaResponse = await fetch(
    `https://api.airbyte.ai/api/v1/integrations/sources/${sourceId}/streams/${selectedStream.name}`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  const schema = await schemaResponse.json();

  // Build dynamic table/form based on schema
  return buildUIFromSchema(schema);
}
```

### Data Validation

Validate that expected fields are available:

```javascript
async function validateRequiredFields(sourceId, streamName, requiredFields, token) {
  const response = await fetch(
    `https://api.airbyte.ai/api/v1/integrations/sources/${sourceId}/streams/${streamName}`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  const schema = await response.json();

  const availableFields = Object.keys(schema.json_schema.properties);
  const missingFields = requiredFields.filter(
    field => !availableFields.includes(field)
  );

  if (missingFields.length > 0) {
    throw new Error(`Missing required fields: ${missingFields.join(', ')}`);
  }

  return true;
}
```

### Schema Monitoring

Monitor schema changes over time:

```javascript
async function detectSchemaChanges(sourceId, previousCatalog, token) {
  const response = await fetch(
    `https://api.airbyte.ai/api/v1/integrations/sources/${sourceId}/catalog/query`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  const currentCatalog = await response.json();

  const changes = {
    addedStreams: [],
    removedStreams: [],
    modifiedStreams: [],
  };

  // Compare catalogs to detect changes
  const previousStreamNames = new Set(previousCatalog.streams.map(s => s.name));
  const currentStreamNames = new Set(currentCatalog.streams.map(s => s.name));

  // Find added streams
  currentCatalog.streams.forEach(stream => {
    if (!previousStreamNames.has(stream.name)) {
      changes.addedStreams.push(stream.name);
    }
  });

  // Find removed streams
  previousCatalog.streams.forEach(stream => {
    if (!currentStreamNames.has(stream.name)) {
      changes.removedStreams.push(stream.name);
    }
  });

  // Find modified streams (simplified - check field count)
  currentCatalog.streams.forEach(currentStream => {
    const previousStream = previousCatalog.streams.find(
      s => s.name === currentStream.name
    );
    if (previousStream) {
      const currentFields = Object.keys(currentStream.json_schema.properties).length;
      const previousFields = Object.keys(previousStream.json_schema.properties).length;
      if (currentFields !== previousFields) {
        changes.modifiedStreams.push(currentStream.name);
      }
    }
  });

  return changes;
}
```

### AI/ML Feature Engineering

Use schema information to build AI features:

```javascript
async function generateFeatureDescriptions(sourceId, streamName, token) {
  const response = await fetch(
    `https://api.airbyte.ai/api/v1/integrations/sources/${sourceId}/streams/${streamName}`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  const schema = await response.json();

  const features = Object.entries(schema.json_schema.properties).map(
    ([fieldName, fieldSchema]) => ({
      name: fieldName,
      type: fieldSchema.type,
      format: fieldSchema.format,
      isNumeric: ['number', 'integer'].includes(fieldSchema.type),
      isTimestamp: fieldSchema.format === 'date-time',
      isPrimaryKey: schema.source_defined_primary_key?.some(
        key => key[0] === fieldName
      ),
    })
  );

  return features;
}
```

## Best Practices

### Caching

Schema discovery can be slow for large sources. Cache results:

```javascript
class SchemaCache {
  constructor(ttlMinutes = 60) {
    this.cache = new Map();
    this.ttl = ttlMinutes * 60 * 1000;
  }

  async getSchema(sourceId, streamName, token) {
    const cacheKey = `${sourceId}:${streamName}`;
    const cached = this.cache.get(cacheKey);

    if (cached && Date.now() - cached.timestamp < this.ttl) {
      return cached.schema;
    }

    const response = await fetch(
      `https://api.airbyte.ai/api/v1/integrations/sources/${sourceId}/streams/${streamName}`,
      { headers: { 'Authorization': `Bearer ${token}` } }
    );
    const schema = await response.json();

    this.cache.set(cacheKey, {
      schema,
      timestamp: Date.now(),
    });

    return schema;
  }
}
```

### Error Handling

Discovery can fail for various reasons:

```javascript
async function discoverSourceSchema(sourceId, token) {
  try {
    // Trigger discovery
    const discoverResponse = await fetch(
      `https://api.airbyte.ai/api/v1/integrations/sources/${sourceId}/discover`,
      {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
      }
    );

    if (!discoverResponse.ok) {
      throw new Error(`Discovery failed: ${discoverResponse.statusText}`);
    }

    // Poll for completion (simplified - use proper polling with backoff)
    await new Promise(resolve => setTimeout(resolve, 5000));

    // Get catalog
    const catalogResponse = await fetch(
      `https://api.airbyte.ai/api/v1/integrations/sources/${sourceId}/catalog/query`,
      { headers: { 'Authorization': `Bearer ${token}` } }
    );

    if (!catalogResponse.ok) {
      throw new Error(`Catalog query failed: ${catalogResponse.statusText}`);
    }

    return await catalogResponse.json();
  } catch (error) {
    console.error('Schema discovery failed:', error);
    throw error;
  }
}
```

### Performance

For sources with many streams, use pagination and filtering:

```javascript
// Get only specific streams
async function getRelevantStreams(sourceId, relevantStreamNames, token) {
  const catalog = await fetch(
    `https://api.airbyte.ai/api/v1/integrations/sources/${sourceId}/catalog/query`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  ).then(r => r.json());

  return catalog.streams.filter(stream =>
    relevantStreamNames.includes(stream.name)
  );
}
```

## Troubleshooting

### Discovery Takes Too Long

**Possible causes:**
- Source has many tables/collections
- Source connection is slow
- Source requires complex authentication

**Solutions:**
- Be patient - first discovery can take several minutes
- Cache results to avoid repeated discoveries
- Check source connection health
- Contact support if discovery consistently times out

### Missing Streams

**Possible causes:**
- User doesn't have permissions in the source system
- Streams are filtered by source configuration
- Schema hasn't been discovered yet

**Solutions:**
- Verify user permissions in the source system
- Check source configuration settings
- Trigger manual discovery
- Wait for initial discovery to complete

### Incorrect Field Types

**Possible causes:**
- Source doesn't provide type information
- Airbyte inferred types from sample data
- Type information is ambiguous

**Solutions:**
- Review the source's native schema
- Use format specifiers for additional context
- Validate data at runtime
- Contact support if types are consistently wrong

## API Reference

- [Discover Source](https://api.airbyte.ai/api/v1/docs#/Integrations/post_api_v1_integrations_sources__id__discover)
- [Query Catalog](https://api.airbyte.ai/api/v1/docs#/Integrations/get_api_v1_integrations_sources__id__catalog_query)
- [List Streams](https://api.airbyte.ai/api/v1/docs#/Integrations/get_api_v1_integrations_sources__id__streams)
- [Get Stream Details](https://api.airbyte.ai/api/v1/docs#/Integrations/get_api_v1_integrations_sources__id__streams__stream_name_)

## Next Steps

- Configure [Source Templates](./source-templates.md)
- Set up [Connection Templates](./connection-templates.md)
- Manage [Workspaces](./workspace-management.md)
- Implement [Authentication](./authentication.md)
