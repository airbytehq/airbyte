# Entity cache

Some APIs have search endpoints, but many don't. This makes search operations resource-intensive. Imagine prompts like these:

- `List all customers closing this month with deal sizes greater than $5000.`
- `Search all dresses and find the ones with a color option of red.`

Even though they're short, they're complex enough to require your agent to do significant work. This can cause a variety of effects:

- Unbounded growth of the context window
- Long-running queries
- Needing to iteratively collect paginated lists of records
- API rate limiting

The result is a query that takes substantial time and resources to process, a degraded experience, and inflated costs.

The entity cache solves this problem by making key fields available to your agents in Airbyte-managed object storage. When you enable it, the entity cache allows AI agents to make object-based queries on your data, based on natural language prompts. Agents can query it with less than half a second of latency.

## Enable the entity cache

To enable the entity cache, follow these steps.

1. In Airbyte's Agent Engine, click Connectors.

2. Enable **Cache connected source data for agentic search**.

When you enable the entity cache:

- **Storage begins automatically**. Airbyte copies a subset of data from your agent connectors to Airbyte-managed storage. Not all data goes into the entity cache. Airbyte selects a subset of your data that it considers relevant to search actions.

- **Search becomes available**. Data from the cache is available via the search action in direct connectors.

Each connected source maintains its own isolated data store. Your data is only accessible to AI agents within your organization.

You can't use the entity cache until Airbyte completes its first full data population. This takes time to complete, according to the volume of data in your connected sources. You can continue using Airbyte while it populates the entity cache.

## Disable the entity cache

To turn off the entity cache, follow these steps.

1. In Airbyte's Agent Engine, click Connectors.

2. Disable **Cache connected source data for agentic search**.

When you turn off the cache, Airbyte removes the cached data from Airbyte storage. AI agents will no longer be able to run search actions on the cache until you re-enable the cache and data syncs again.

## Query the entity cache via API

Once the entity cache is enabled and populated, you can query it programmatically using the search API. This allows your applications and AI agents to execute structured queries against cached data with sub-second latency.

### Discover available streams and fields

Before querying, discover what data is available in the cache.

#### List available streams

```http
GET /api/v1/integrations/connectors/{connector_id}/streams
```

Returns metadata about all cached streams for a source, such as `contacts`, `deals`, or `issues`.

#### Get field metadata for a stream

```http
GET /api/v1/integrations/connectors/{connector_id}/streams/{stream_name}/fields
```

Returns field names and types for a specific stream, helping you build valid queries.

### Search endpoint

```http
POST /api/v1/integrations/connectors/{connector_id}/search/{stream_name}
```

Replace `{connector_id}` with your source's ID and `{stream_name}` with the entity you want to query.

### Request format

The following example shows a complete curl request to search for active contacts:

```bash
curl -X POST "https://api.airbyte.com/api/v1/integrations/connectors/{connector_id}/search/contacts" \
  -H "Authorization: Bearer {your_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "filter": { "eq": { "status": "active" } },
      "sort": [{ "created_at": "desc" }]
    },
    "limit": 100,
    "cursor": null,
    "fields": ["id", "name", "email"]
  }'
```

The request body contains the following fields.

| Field | Type | Description |
|-------|------|-------------|
| `query.filter` | object | Optional filter condition. If omitted, returns all records. |
| `query.sort` | array | Optional sort order. Each element maps a field name to `asc` or `desc`. |
| `limit` | integer | Maximum results to return (default: 1000). |
| `cursor` | string | Pagination cursor from a previous response. |
| `fields` | array | Field names to include in results. Supports dot notation for nested fields. |

### Filter operators

The search API supports a rich set of filter operators for building queries.

#### Comparison operators

| Operator | Description | Example |
|----------|-------------|---------|
| `eq` | Equal to | `{"eq": {"status": "active"}}` |
| `neq` | Not equal to | `{"neq": {"status": "closed"}}` |
| `gt` | Greater than | `{"gt": {"amount": 1000}}` |
| `gte` | Greater than or equal | `{"gte": {"created_at": "2024-01-01"}}` |
| `lt` | Less than | `{"lt": {"priority": 3}}` |
| `lte` | Less than or equal | `{"lte": {"age": 65}}` |
| `in` | Value in list | `{"in": {"status": ["open", "pending"]}}` |

#### Text search operators

| Operator | Description | Example |
|----------|-------------|---------|
| `like` | Pattern match with `%` wildcards | `{"like": {"name": "%smith%"}}` |
| `fuzzy` | Ordered word match (case-insensitive) | `{"fuzzy": {"description": "quarterly report"}}` |
| `keyword` | Any word present (case-insensitive) | `{"keyword": {"notes": "urgent priority"}}` |

#### Logical operators

| Operator | Description | Example |
|----------|-------------|---------|
| `and` | All conditions must match | `{"and": [{"eq": {"status": "active"}}, {"gt": {"amount": 100}}]}` |
| `or` | Any condition must match | `{"or": [{"eq": {"type": "lead"}}, {"eq": {"type": "contact"}}]}` |
| `not` | Negates a condition | `{"not": {"eq": {"status": "archived"}}}` |

#### Nested data operators

| Operator | Description | Example |
|----------|-------------|---------|
| `has` | Access nested object fields | `{"has": {"metadata": {"eq": {"version": "2.0"}}}}` |
| `any` | Match any element in an array | `{"any": {"tags": {"eq": {"name": "premium"}}}}` |
| `contains` | Check if value exists in array | `{"contains": {"labels": "important"}}` |

#### Dot notation shorthand

You can use dot notation as a shorthand for nested field access. The API automatically expands dot notation to the equivalent `has` structure.

```json
{"eq": {"user.address.city": "Seattle"}}
```

This is equivalent to:

```json
{"has": {"user": {"has": {"address": {"eq": {"city": "Seattle"}}}}}}
```

### Response format

```json
{
  "hits": [
    {
      "id": "abc123",
      "score": null,
      "data": {
        "id": "abc123",
        "name": "Acme Corp",
        "email": "contact@acme.com"
      }
    }
  ],
  "next_cursor": "eyJvZmZzZXQiOjEwMH0=",
  "took_ms": 45
}
```

The response contains the following fields.

| Field | Type | Description |
|-------|------|-------------|
| `hits` | array | Array of matching records. Each hit contains `id`, `score`, and `data`. |
| `next_cursor` | string | Cursor for fetching the next page. Null if no more results. |
| `took_ms` | integer | Query execution time in milliseconds. |

### Example: Find high-value deals closing this month

```bash
curl -X POST "https://api.airbyte.com/api/v1/integrations/connectors/{connector_id}/search/deals" \
  -H "Authorization: Bearer {your_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "filter": {
        "and": [
          {"gte": {"amount": 50000}},
          {"gte": {"close_date": "2024-03-01"}},
          {"lte": {"close_date": "2024-03-31"}},
          {"eq": {"stage": "negotiation"}}
        ]
      },
      "sort": [{"amount": "desc"}]
    },
    "limit": 50,
    "fields": ["id", "name", "amount", "close_date", "owner.name"]
  }'
```

## Notes and limitations

- You may choose to avoid enabling the entity cache if you have configured your own object storage. If you already have a copy of key pieces of customer data, make this available to your agents via self-implemented tools.

- Data refreshes hourly. You can't configure the refresh rate, but you can turn off the entity cache if you need to.

- All agent connectors can use the entity cache. Limited, temporary exceptions to this rule are possible, however.

- The search API only queries data in the entity cache. If you replicate data to your own destination, you query that data directly using your destination's native query capabilities.
