# Dynamic Streams

Dynamic streams enable manifest-only connectors to generate streams at runtime based on external data sources such as API responses or user configuration. This powerful feature allows connectors to adapt to varying API structures and user requirements without hardcoding every possible stream.

## Overview

Dynamic streams are implemented using `DynamicDeclarativeStream` with component resolvers that fetch stream configuration values from external sources. Unlike static [Stream Templates](./stream-templates.md) that use predefined parameter sets, dynamic streams determine their configuration at runtime.

```yaml
dynamic_streams:
  - type: DynamicDeclarativeStream
    stream_template:
      type: DeclarativeStream
      name: "{{ stream_name }}"  # Will be populated dynamically
      retriever:
        # Template configuration with placeholders
    components_resolver:
      # Resolver that fetches values from external sources
```

## Component Resolvers

Dynamic streams use three types of component resolvers to fetch configuration values:

### HttpComponentsResolver

Fetches stream configuration from API responses. This is useful when the API provides metadata about available streams or when stream parameters depend on API responses.

Here's an example from the Google Search Console connector that creates custom report streams:

```yaml
dynamic_streams:
  - type: DynamicDeclarativeStream
    stream_template:
      type: DeclarativeStream
      name: "search_analytics_by_custom_dimensions"
      primary_key:
        - site_url
        - search_type
      retriever:
        type: SimpleRetriever
        requester:
          type: HttpRequester
          url_base: "https://www.googleapis.com/webmasters/v3"
          path: "/sites/{{ sanitize_url(stream_partition.get('site_url')) }}/searchAnalytics/query"
          http_method: POST
          request_body_json:
            startDate: "{{ stream_interval.get('start_time') }}"
            endDate: "{{ stream_interval.get('end_time') }}"
            dimensions: "{{ dimensions }}"  # Will be replaced dynamically
            type: "{{ stream_partition.get('search_type') }}"
        partition_router:
          - type: ListPartitionRouter
            values: "{{ config['site_urls'] }}"
            cursor_field: site_url
          - type: ListPartitionRouter
            values: ["web", "news", "image", "video"]
            cursor_field: search_type
    components_resolver:
      type: HttpComponentsResolver
      retriever:
        type: SimpleRetriever
        requester:
          type: HttpRequester
          url_base: "https://www.googleapis.com/webmasters/v3"
          path: "/custom-reports"
        record_selector:
          type: RecordSelector
          extractor:
            type: DpathExtractor
            field_path: ["reports"]
      components_mapping:
        stream_name: "{{ response.name }}"
        dimensions: "{{ response.dimensions }}"
        primary_key: "{{ response.key_fields }}"
```

The `HttpComponentsResolver` makes an API call to fetch available custom reports, then uses the response to populate the stream template with the actual report configurations.

### ConfigComponentsResolver

Uses values from the user's connector configuration. This allows users to define their own streams through the connector's configuration interface.

Here's an example from the Google Sheets connector that creates streams for user-specified spreadsheets:

```yaml
dynamic_streams:
  - type: DynamicDeclarativeStream
    stream_template:
      type: DeclarativeStream
      name: "{{ stream_name }}"
      primary_key: ["_airbyte_row_num"]
      retriever:
        type: SimpleRetriever
        requester:
          type: HttpRequester
          url_base: "https://sheets.googleapis.com/v4/spreadsheets"
          path: "/{{ spreadsheet_id }}/values/{{ sheet_name }}"
          authenticator: "#/definitions/authenticator"
        record_selector:
          type: RecordSelector
          extractor:
            type: DpathExtractor
            field_path: ["values"]
    components_resolver:
      type: ConfigComponentsResolver
      stream_config: "{{ config['spreadsheet_configs'] }}"
      components_mapping:
        stream_name: "{{ stream_config.name }}"
        spreadsheet_id: "{{ stream_config.spreadsheet_id }}"
        sheet_name: "{{ stream_config.sheet_name }}"
```

In this example, users can configure multiple spreadsheets in their connector configuration, and each one becomes a separate stream.

### ParametrizedComponentsResolver

While primarily used for static templates, `ParametrizedComponentsResolver` can also support dynamic scenarios when the parameter list is generated programmatically. See [Stream Templates](./stream-templates.md) for detailed examples.

## Configuration Mapping

The `components_mapping` section defines how values from the resolver's data source map to placeholders in the stream template:

```yaml
components_mapping:
  # Template placeholder: Source value expression
  stream_name: "{{ response.report_name }}"
  api_endpoint: "{{ response.endpoint_url }}"
  primary_key: "{{ response.key_fields }}"
  schema_fields: "{{ response.schema.fields }}"
```

### Mapping Expressions

- Use Jinja2 template syntax for dynamic value extraction
- Access resolver data through context variables (`response`, `stream_config`, etc.)
- Apply transformations and filters as needed
- Handle nested data structures with dot notation

## Advanced Patterns

### Conditional Stream Generation

Use conditions to control when streams are generated:

```yaml
components_resolver:
  type: ConfigComponentsResolver
  stream_config: "{{ config['custom_streams'] }}"
  components_mapping:
    stream_name: "{{ stream_config.name }}"
    enabled: "{{ stream_config.get('enabled', true) }}"
  # Only generate streams where enabled is true
```

### Schema Transformation

Transform API schemas to match your stream requirements:

```yaml
components_mapping:
  stream_name: "{{ response.name | lower | replace(' ', '_') }}"
  schema_fields: "{{ response.fields | map('extract_field_info') | list }}"
  primary_key: "{{ response.key_field | default('id') }}"
```

### Multi-level Nesting

Handle complex nested configurations:

```yaml
components_mapping:
  stream_name: "{{ stream_config.metadata.display_name }}"
  api_config:
    endpoint: "{{ stream_config.api.endpoint }}"
    method: "{{ stream_config.api.method | default('GET') }}"
    headers: "{{ stream_config.api.headers | default({}) }}"
```

## Best Practices

### Performance Considerations

1. **Cache resolver responses**: Avoid making the same API calls repeatedly
2. **Limit stream generation**: Don't generate excessive numbers of streams
3. **Use efficient selectors**: Optimize record extraction from resolver responses
4. **Handle rate limits**: Implement appropriate delays for resolver API calls

### Error Handling

1. **Validate resolver data**: Check that required fields are present
2. **Provide fallbacks**: Use default values when optional fields are missing
3. **Handle API failures**: Gracefully handle resolver API errors
4. **Log generation issues**: Provide clear error messages for debugging

### Security

1. **Validate user input**: Sanitize configuration values used in stream generation
2. **Limit API access**: Ensure resolver APIs have appropriate authentication
3. **Avoid injection**: Be careful with dynamic path and parameter construction

## Common Use Cases

### Custom Reporting APIs

Many APIs allow users to create custom reports with varying schemas:

```yaml
# Generate streams for user-defined reports
components_resolver:
  type: HttpComponentsResolver
  # Fetch available custom reports from API
components_mapping:
  stream_name: "custom_report_{{ response.id }}"
  report_config: "{{ response.configuration }}"
  schema_fields: "{{ response.schema }}"
```

### Multi-tenant SaaS APIs

For APIs serving multiple tenants or organizations:

```yaml
# Generate streams for each accessible tenant
components_resolver:
  type: HttpComponentsResolver
  # Fetch list of accessible tenants
components_mapping:
  stream_name: "{{ response.tenant_name }}_data"
  tenant_id: "{{ response.tenant_id }}"
  api_base: "{{ response.api_endpoint }}"
```

### User-configured Data Sources

Allow users to specify their own data sources:

```yaml
# Generate streams for user-specified databases/tables
components_resolver:
  type: ConfigComponentsResolver
  stream_config: "{{ config['data_sources'] }}"
components_mapping:
  stream_name: "{{ stream_config.table_name }}"
  connection_string: "{{ stream_config.connection }}"
  query: "{{ stream_config.sql_query }}"
```

## Related Documentation

- [Stream Templates](./stream-templates.md) - Static stream template patterns
- [YAML Overview](./yaml-overview.md) - Understanding the overall YAML structure
- [Partition Router](./partition-router.md) - Handling multiple data partitions
- [Record Selector](./record-selector.md) - Extracting records from API responses
