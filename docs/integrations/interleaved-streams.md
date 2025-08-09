# Interleaved Streams in Airbyte Connectors

## Overview

Interleaved streams are streams that are faster to pull together than they are to pull separately. This concept is most commonly found in API sources where parent-child stream relationships exist, allowing child streams to leverage data from parent streams for more efficient data extraction.

## What Are Interleaved Streams?

Interleaved streams typically exhibit parent-child relationships where:
- **Parent streams** provide essential data (like IDs or configuration) needed by child streams
- **Child streams** depend on parent stream records to make API calls or filter data
- **Performance benefit** comes from avoiding redundant API calls and leveraging cached parent data

### Common Patterns

1. **Simple Parent-Child**: One parent stream feeds multiple child streams
2. **Multi-level Dependencies**: Parent → Child → Grandchild relationships
3. **Cross-dependencies**: Streams that can be interleaved in multiple ways

## Detection in Airbyte Connectors

Airbyte connectors built on the low-code YAML manifest framework use `SubstreamPartitionRouter` to implement parent-child relationships. These can be automatically detected through the following patterns:

### Primary Detection Heuristics

1. **SubstreamPartitionRouter Usage**
   ```yaml
   partition_router:
     type: SubstreamPartitionRouter
     parent_stream_configs:
       - type: ParentStreamConfig
         parent_key: id
         partition_field: parent_id
         stream: "#/definitions/parent_stream"
   ```

2. **Performance Indicators**
   - `incremental_dependency: true` - Indicates performance-critical relationships
   - `GroupingPartitionRouter` wrapping SubstreamPartitionRouter - Suggests optimization needs
   - Multiple parent streams in single configuration - Complex dependencies

### Examples from Production Connectors

#### TikTok Marketing Connector
```yaml
# advertisers_stream (parent) → campaigns, ads, pixels (children)
partition_router:
  type: SubstreamPartitionRouter
  parent_stream_configs:
    - type: ParentStreamConfig
      parent_key: advertiser_id
      partition_field: advertiser_id
      stream: "#/definitions/advertisers_stream"
```

**Interleaved streams**: `[["advertisers", "campaigns", "ads", "pixels"]]`

#### HubSpot Connector
```yaml
# forms_stream (parent) → form_submissions (child)
underlying_partition_router:
  type: SubstreamPartitionRouter
  parent_stream_configs:
    - type: ParentStreamConfig
      stream: "#/definitions/forms_stream"
      parent_key: "id"
      partition_field: "form_id"
```

**Interleaved streams**: `[["forms", "form_submissions"]]`

#### Instagram Connector
```yaml
# Api (parent) → Media (child) → MediaInsights (grandchild)
partition_router:
  type: SubstreamPartitionRouter
  parent_stream_configs:
    - type: ParentStreamConfig
      parent_key: account
      partition_field: account
      stream: "#/definitions/streams/Api"
```

**Interleaved streams**: `[["Api", "Media", "MediaInsights"]]`

## Metadata Documentation

### metadata.yaml Extension

To document interleaved streams, extend the existing `metadata.yaml` structure with an `interleavedStreams` section:

```yaml
data:
  # ... existing metadata fields ...
  interleavedStreams:
    # List of lists - each sublist contains streams that should be processed together
    relationships:
      - ["advertisers", "campaigns", "ads", "pixels"]
      - ["forms", "form_submissions"]
      - ["Api", "Media", "MediaInsights"]
    
    # Optional: Additional optimization hints
    optimizationHints:
      parallelizable: ["profiles", "metrics"]  # Independent streams
      performanceCritical: ["advertisers", "campaigns"]  # High-impact relationships
```

### Structure Explanation

- **List of Lists**: Each inner list represents streams that are interleaved together
- **Multiple Relationships**: Streams can appear in multiple sublists if they have different interleaving patterns
- **Optimization Hints**: Additional metadata for sync orchestration decisions

### Example: Complex GitHub-style Relationships
```yaml
interleavedStreams:
  relationships:
    - ["issues", "issue_comments", "issue_comment_reactions"]
    - ["issues", "issue_reactions"]
    - ["pull_requests", "pull_request_reviews", "pull_request_review_comments"]
```

In this example:
- `issues` is interleaved with both comment-related streams AND reaction streams
- Each sublist represents a different interleaving pattern
- Streams can participate in multiple interleaved relationships

## Performance Implications

### Benefits of Proper Interleaving

1. **Reduced API Calls**: Child streams leverage cached parent data
2. **Better Rate Limit Management**: Coordinated requests avoid hitting limits
3. **Improved Incremental Sync**: Parent state can guide child stream updates
4. **Memory Efficiency**: Shared partition data reduces memory overhead

### Optimization Strategies

1. **Sequential Processing**: Process interleaved streams in dependency order
2. **Caching**: Parent stream data is automatically cached for child streams
3. **Incremental Dependencies**: Use `incremental_dependency: true` for performance-critical relationships
4. **Grouping**: Use `GroupingPartitionRouter` to batch partition processing

## Implementation Guide

### For Connector Developers

1. **Identify Dependencies**: Map out parent-child relationships in your API
2. **Use SubstreamPartitionRouter**: Implement using the declarative framework
3. **Set Performance Flags**: Use `incremental_dependency: true` for critical relationships
4. **Document in Metadata**: Add `interleavedStreams` section to metadata.yaml

### For Platform Developers

1. **Detection**: Scan manifest.yaml files for SubstreamPartitionRouter patterns
2. **Validation**: Ensure declared interleaved streams match manifest configuration
3. **Orchestration**: Use metadata for sync parallelization decisions
4. **Monitoring**: Track performance improvements from proper interleaving

## Quality Assurance

### Automated Checks

The `connectors_qa` tool includes checks for:
- **Undeclared Interleaved Streams**: Detects SubstreamPartitionRouter usage without corresponding metadata
- **Metadata Validation**: Ensures interleaved stream declarations are accurate
- **Performance Verification**: Validates incremental_dependency flags are properly set

### Manual Review Guidelines

1. **Verify Relationships**: Confirm parent-child relationships match API behavior
2. **Test Performance**: Measure sync times with and without interleaving
3. **Check Edge Cases**: Ensure proper handling of empty parent streams
4. **Validate Incremental**: Test incremental sync behavior for dependent streams

## Migration Guide

### Existing Connectors

1. **Audit Current Usage**: Scan for existing SubstreamPartitionRouter patterns
2. **Add Metadata**: Document discovered relationships in metadata.yaml
3. **Optimize Configuration**: Add performance flags where appropriate
4. **Test Thoroughly**: Verify no regression in sync behavior

### New Connectors

1. **Design Phase**: Identify interleaved patterns during API analysis
2. **Implementation**: Use SubstreamPartitionRouter from the start
3. **Documentation**: Include interleavedStreams in initial metadata.yaml
4. **Validation**: Run connectors_qa checks before submission

## Statistics

Based on analysis of the Airbyte connector ecosystem:
- **243+ connectors** use SubstreamPartitionRouter for parent-child relationships
- **29 connectors** use `incremental_dependency: true` for performance optimization
- **Common patterns** include advertiser→campaigns, forms→submissions, accounts→resources

## Future Enhancements

1. **Dynamic Detection**: Runtime analysis of API call patterns
2. **Performance Metrics**: Automated measurement of interleaving benefits
3. **Smart Orchestration**: AI-driven sync optimization based on interleaving metadata
4. **Cross-Connector Patterns**: Shared interleaving strategies across similar APIs
