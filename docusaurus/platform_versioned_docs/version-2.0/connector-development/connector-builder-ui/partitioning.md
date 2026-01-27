# Partitioning

Partitioning is required when records of a stream are grouped into subsets that need to be queried separately to extract all records. This is common when APIs require specific parameters (like IDs or categories) to fetch different portions of the data.

The Connector Builder UI provides a unified partitioning interface that supports multiple partition router types. All partitioning configuration is done through the **Partition Router** section in the stream configuration.

## Partition Router Types

The Connector Builder supports four types of partition routers, each designed for different API patterns:

### List Partition Router

Use this when you have a static list of values to iterate over, either defined in the connector or provided by the user.

**Configuration:**
- **Partition Values**: Either a static list of strings or a reference to user input
- **Current Partition Value Identifier**: Field name to reference the current partition value (e.g., `{{ stream_partition.section }}`)
- **Inject Partition Value Into Outgoing HTTP Request**: How to add the partition value to requests

**Example - Static List:**
For the SurveySparrow API responses endpoint that requires a `survey_id` parameter:
- Set Partition Values to `["123", "456", "789"]`
- Set Current Partition Value Identifier to `survey`
- Configure injection as request parameter `survey_id`

This generates requests:
```
GET https://api.surveysparrow.com/v3/responses?survey_id=123
GET https://api.surveysparrow.com/v3/responses?survey_id=456
GET https://api.surveysparrow.com/v3/responses?survey_id=789
```

**Example - User Input:**
To let users specify which surveys to sync:
- Set Partition Values to user input reference: `{{ config['survey_ids'] }}`
- Create a user input of type array named `survey_ids`

### Substream Partition Router

Use this when partition values come from records of another stream (parent-child relationship).

**Configuration:**
- **Parent Stream**: Select which stream provides the partition values
- **Parent Key**: Field from parent records to use as partition value (e.g., `id`)
- **Partition Field**: Identifier to reference the partition value (e.g., `{{ stream_partition.parent_id }}`)
- **Incremental Dependency**: Whether parent stream should be read incrementally
- **Request Option**: How to inject the partition value into requests

**Example:**
For WooCommerce order notes that require an order ID in the path:
- Parent Stream: `orders`
- Parent Key: `id`
- Partition Field: `order_id`
- URL Path: `/orders/{{ stream_partition.order_id }}/notes`

### Custom Partition Router

Use this for complex partitioning logic that requires custom Python code.

**Configuration:**
- **Class Name**: Fully-qualified Python class name (e.g., `source_myapi.components.MyPartitionRouter`)

This router type requires implementing custom logic in your connector's Python code.

### Grouping Partition Router

Use this to batch multiple partitions together for APIs that support filtering by multiple values in a single request.

**Configuration:**
- **Group Size**: Number of partitions to include in each batch
- **Underlying Partition Router**: The base partition router to group (can be any other type)
- **Deduplicate Partitions**: Whether to remove duplicate partition values within groups

**Note:** Per-partition incremental syncs may not work as expected with grouping since partition groupings might change between syncs.

### Multiple Partition Routers

You can configure multiple partition routers on a single stream. When multiple routers are used, all possible combinations of partition values are requested separately.

**Example:**
For Google PageSpeed API that requires both `url` and `strategy` parameters:
- First router: URLs `["example.com", "example.org"]`
- Second router: Strategies `["desktop", "mobile"]`

This generates all combinations:
```
GET https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=example.com&strategy=desktop
GET https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=example.com&strategy=mobile
GET https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=example.org&strategy=desktop
GET https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=example.org&strategy=mobile
```

## Advanced Configuration

### Adding Partition Values to Records

You can add the partition value to each record using transformations:
1. Set the partition field identifier (e.g., `order_id`)
2. Add an "Add field" transformation with path `partition_value` and value `{{ stream_partition.order_id }}`

### Custom Parameter Injection

For complex injection requirements that the standard options don't support:
1. Disable injection in the partition router configuration
2. Use the stream's parameter section to configure custom headers, query parameters, or request body fields
3. Reference partition values using `{{ stream_partition.your_field }}` syntax

### Parent Stream Advanced Features

**Extra Fields**: Include additional fields from parent records in stream slices:
- Configure field paths as arrays (e.g., `[["name"], ["category", "type"]]`)
- Access via `{{ stream_slice.extra_fields.name }}`

**Lazy Read Pointer**: Enable lazy reading to extract child records during initial parent record processing.

**Incremental Dependency**: When enabled, the parent stream is read incrementally based on child stream updates.

## When not to Use Partitioning

Don't use partitioning for:
- **Pagination**: Use the Pagination feature instead
- **Time-based incremental sync**: Use the Incremental Sync feature instead

Partitioning is specifically for cases where the API requires different parameter values to access different subsets of the same logical data stream.
