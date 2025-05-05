# Stream Templates

## Overview

Stream Templates (also known as Dynamic Streams) allow you to generate multiple similar streams from a single template configuration. This is particularly useful when an API has multiple endpoints that follow the same structure but with different parameters or identifiers.

## When to use Stream Templates

Stream templates are ideal for scenarios like:

- APIs that have endpoints for multiple resources with identical structures
- APIs where you need to fetch data from multiple regions or geographical areas using the same endpoint pattern
- APIs that provide the same data structure for different resources (e.g., metrics for different entities)

## How Stream Templates work

A stream template consists of two main sections:

1. **Fetch Data for Template** - Fetches a list of items from an API endpoint
2. **Generated Stream Template** - Defines how each generated stream will behave, using values from the items fetched in the first section

## Step-by-Step Setup Guide

### 1. Create a new Stream Template

1. In the Connector Builder UI, click the `+` button next to `Stream Templates`.
2. Enter a name for your template (e.g. `Project Metrics`).
3. Enter the URL path for fetching the data that will be used to generate individual streams. (e.g. `/projects`)

### 2. Configure Fetch Data for Template

This fetches the list of items that will be used to generate individual streams.

1. In the "Fetch Data for Template" section, configure:
   - **URL Path**: The endpoint that returns the list of items (e.g., `/api/projects`)
   - **Record Selector**: How to extract records from the response
     - **Field Path**: The JSON path to the array of items (e.g., `results, data`)
     - **Record Filter** (optional): A condition to filter specific records

2. Click `Preview endpoint` in the right-hand testing panel to test the `Fetch Data for Template` configuration and see what data it returns.

### 3. Configure Generated Stream Template

In the `Generated Stream Template` section, define how each generated stream will be configured:

1. Set up the stream configuration just like you would for a regular stream.
2. Use references to values from the previous step records with `{{ components_values.field_name }}`.
   - For example, if each project has an `id` field that you need to use as part of the generated streams' URL paths, you can put `projects/{{ components_values.id }}/metrics` in the Generated Stream Template URL path

### 4. Generate Streams

After configuring both parts:

1. Click "Generate Streams" to create individual streams based on the template.
2. The generated streams will appear in the left-hand sidebar under the corresponding stream template. Click the `>` in the stream template to expand and see the generated streams.
3. Test individual generated streams to verify they work correctly.

:::info

The generated streams are read-only; to make changes to them, you must modify the parent Stream Template configuration, and re-generate the streams.

:::

## Example: Project Metrics API

Imagine an analytics API where you can fetch the same metrics for different projects:

### Step 1: Configure the Retriever

**URL Path**: `/api/projects`

The API returns:
```json
{
  "projects": [
    {
      "id": "project-123",
      "name": "Web Application"
    },
    {
      "id": "project-456",
      "name": "Mobile Application"
    }
  ]
}
```

**Record Selector**:
- Field Path: `projects`

### Step 2: Configure the Stream Template

**Stream Template Configuration**:
- URL Path: `/api/projects/{{ components_values.id }}/metrics`
- Stream name: `{{ components_values.name }} Metrics`
- (Configure other stream settings as needed)

### Step 3: Generate Streams

After clicking "Generate Streams", you'll get two streams:
1. "Web Application Metrics" with URL path `/api/projects/project-123/metrics`
2. "Mobile Application Metrics" with URL path `/api/projects/project-456/metrics`

## Important Notes

- **Testing**: Always test both the retriever and the generated streams before publishing
- **Changes**: If you modify the stream template, you'll need to regenerate streams for changes to take effect
- **Troubleshooting**: If generated streams show warnings, fix issues in the template and regenerate
- **References**: Use `{{ components_values.field_name }}` to access fields from the retriever results
- **Editing Generated Streams**: Generated streams are read-only; changes must be made to the template

## Limitations

In the current UI, you can only configure:
- The stream template name
- The URL path for the retriever
- The record selector for the retriever (field path and optional record filter)
- The stream template configuration
