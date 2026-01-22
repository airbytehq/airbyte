# Stream Templates

Stream templates provide a powerful way to define reusable stream configurations in manifest-only connectors. They allow you to create template streams that can be populated with different values to generate multiple similar streams, making your connector configuration more maintainable and reducing duplication.

## Overview

A stream template is defined using the `DynamicDeclarativeStream` type, which accepts a `stream_template` containing a standard `DeclarativeStream` configuration with placeholder values. These placeholders are then populated by a `components_resolver` to create one or more actual streams.

```yaml
dynamic_streams:
  - type: DynamicDeclarativeStream
    stream_template:
      type: DeclarativeStream
      name: "{{ stream_name }}"  # Placeholder to be replaced
      retriever:
        # Standard retriever configuration with placeholders
    components_resolver:
      # Resolver that provides values for the placeholders
```

Stream templates are useful in two main scenarios:

1. **Static use cases**: Creating multiple similar streams with predefined variations (DRY principle)
2. **Dynamic use cases**: Generating streams at runtime based on API responses or user configuration

For dynamic runtime generation patterns, see the [Dynamic Streams](./dynamic-streams.md) documentation.

## Static Stream Templates

Static stream templates help reduce duplication when you need multiple similar streams with predefined variations. This is particularly useful for APIs that have similar endpoints with different parameters.

### Using ParametrizedComponentsResolver

The `ParametrizedComponentsResolver` allows you to define a list of parameter sets that will be used to generate multiple streams from a single template.

Here's an example from the Bing Ads connector that creates multiple report streams:

```yaml
dynamic_streams:
  - type: DynamicDeclarativeStream
    stream_template:
      type: DeclarativeStream
      name: "{{ stream_name }}"
      primary_key:
        - AccountId
        - "{{ primary_key }}"
      retriever:
        type: SimpleRetriever
        requester:
          type: HttpRequester
          path: "/Reporting/v13/ReportingService.svc"
          request_body_json:
            ReportRequest:
              ReportType: "{{ report_type }}"
              ReportName: "{{ report_name }}"
              Columns: "{{ report_columns }}"
        record_selector:
          type: RecordSelector
          extractor:
            type: DpathExtractor
            field_path: ["Report", "Table", "Row"]
    components_resolver:
      type: ParametrizedComponentsResolver
      stream_parameters:
        - stream_name: "age_gender_audience_report_hourly"
          report_type: "AgeGenderAudienceReportRequest"
          report_name: "Age Gender Audience Report Hourly"
          report_columns: ["TimePeriod", "AccountId", "Age", "Gender"]
          primary_key: ["TimePeriod"]
        - stream_name: "age_gender_audience_report_daily"
          report_type: "AgeGenderAudienceReportRequest" 
          report_name: "Age Gender Audience Report Daily"
          report_columns: ["TimePeriod", "AccountId", "Age", "Gender"]
          primary_key: ["TimePeriod"]
```

This configuration generates two separate streams (`age_gender_audience_report_hourly` and `age_gender_audience_report_daily`) from a single template, each with different parameter values.

### Benefits of Static Templates

- **Reduced duplication**: Define common configuration once and reuse it
- **Easier maintenance**: Changes to the template automatically apply to all generated streams
- **Consistent structure**: Ensures all similar streams follow the same pattern
- **Clear organization**: Groups related streams together in the configuration

## Dynamic Stream Templates

Dynamic stream templates generate streams at runtime based on external data sources. This is covered in detail in the [Dynamic Streams](./dynamic-streams.md) documentation, but here's a brief overview of the available resolvers:

### HttpComponentsResolver

Fetches stream configuration values from API responses:

```yaml
components_resolver:
  type: HttpComponentsResolver
  retriever:
    # HTTP retriever configuration
  components_mapping:
    stream_name: "{{ response.name }}"
    # Map API response fields to template placeholders
```

### ConfigComponentsResolver  

Uses values from the user's connector configuration:

```yaml
components_resolver:
  type: ConfigComponentsResolver
  stream_config: "{{ config['custom_reports'] }}"
  components_mapping:
    stream_name: "{{ stream_config.name }}"
    # Map config values to template placeholders
```

## Best Practices

1. **Use descriptive placeholder names**: Choose placeholder names that clearly indicate what they represent
2. **Keep templates focused**: Each template should represent a single pattern or type of stream
3. **Document your placeholders**: Include comments explaining what each placeholder expects
4. **Test with multiple parameter sets**: Ensure your template works correctly with all intended parameter combinations
5. **Consider schema variations**: If generated streams have different schemas, handle this in your template design

## Common Patterns

### Report-style APIs
Many APIs offer similar report endpoints with different parameters. Stream templates are perfect for these:

```yaml
stream_template:
  name: "{{ report_name }}_report"
  retriever:
    requester:
      path: "/reports/{{ report_type }}"
      request_body_json:
        report_type: "{{ report_type }}"
        columns: "{{ columns }}"
```

### Multi-tenant APIs
For APIs that serve multiple tenants or accounts:

```yaml
stream_template:
  name: "{{ tenant_id }}_{{ resource_type }}"
  retriever:
    requester:
      path: "/tenants/{{ tenant_id }}/{{ resource_type }}"
```

### Parameterized endpoints
For APIs with multiple similar endpoints:

```yaml
stream_template:
  name: "{{ endpoint_name }}"
  retriever:
    requester:
      path: "/api/v1/{{ endpoint_path }}"
      request_parameters:
        type: "{{ endpoint_type }}"
```

## Related Documentation

- [Dynamic Streams](./dynamic-streams.md) - Runtime stream generation patterns
- [YAML Overview](./yaml-overview.md) - Understanding the overall YAML structure
- [Partition Router](./partition-router.md) - Handling multiple data partitions
