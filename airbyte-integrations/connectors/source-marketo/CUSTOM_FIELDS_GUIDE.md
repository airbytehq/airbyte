# Marketo Custom Fields Support

## Overview

The Marketo connector now supports **dynamic discovery and extraction of custom fields** in the Leads stream. This enhancement allows you to extract all your custom fields without manually updating the schema or connector code.

## What's New

### Before
- Only static schema fields defined in `leads.json` were supported
- Custom fields were ignored during extraction
- Manual schema updates required for new custom fields

### After
- **All available fields** (standard + custom) are automatically discovered
- **Dynamic schema generation** based on Marketo API field descriptions
- **Automatic data type mapping** for proper field handling
- **No manual configuration** required for new custom fields

## How It Works

The connector now:

1. **Calls Marketo's `leads/describe.json` API** to discover all available fields
2. **Generates a dynamic schema** with proper data type mapping
3. **Extracts all discovered fields** during sync operations
4. **Maintains backward compatibility** with fallback to static schema

## Supported Field Types

The connector automatically maps Marketo field types to appropriate JSON schema types:

| Marketo Type | JSON Schema Type | Format | Example |
|--------------|------------------|--------|---------|
| `integer`, `score`, `percent` | `integer` | - | `42` |
| `float`, `currency` | `number` | - | `123.45` |
| `boolean` | `boolean` | - | `true` |
| `date` | `string` | `date` | `"2023-12-25"` |
| `datetime` | `string` | `date-time` | `"2023-12-25T10:30:00Z"` |
| `email` | `string` | `email` | `"user@example.com"` |
| `url` | `string` | `uri` | `"https://example.com"` |
| `string`, `text`, `textarea`, `phone` | `string` | - | `"Sample text"` |

## Usage

### No Configuration Required

The custom fields support is **automatically enabled** - no additional configuration is needed in your Airbyte connection.

### Viewing Available Fields

When you set up or refresh your Marketo connection in Airbyte:

1. The connector will automatically discover all available fields
2. Both standard and custom fields will appear in the schema
3. Custom fields typically have names ending with `__c` (e.g., `customScore__c`)

### Example Custom Fields

Common custom field examples you might see:
```json
{
  "leadSource__c": "Website Form",
  "marketingQualified__c": true,
  "customerScore__c": 85,
  "lastTouchDate__c": "2023-12-01T15:30:00Z",
  "customIndustry__c": "Technology",
  "annualContractValue__c": 50000.00
}
```

## Benefits

### ✅ Automatic Discovery
- New custom fields are automatically included in syncs
- No need to update connector code or schema files
- Works with any number of custom fields

### ✅ Proper Data Types
- Maintains data integrity with correct type mapping
- Supports all Marketo field types
- Proper formatting for dates, emails, URLs

### ✅ Backward Compatible
- Existing connections continue to work
- Falls back to static schema if API calls fail
- No breaking changes to current functionality

### ✅ Performance Optimized
- Single API call to discover all fields
- Efficient field mapping and extraction
- Minimal overhead added to sync process

## Troubleshooting

### Missing Custom Fields

If custom fields are not appearing:

1. **Check Marketo Permissions**: Ensure your API user has permission to access custom fields
2. **Verify Field Visibility**: Custom fields must be visible via REST API in Marketo
3. **Refresh Connection**: Try refreshing your Airbyte connection to re-discover fields

### Schema Issues

If you encounter schema-related errors:

1. **Check Logs**: Look for warnings about field discovery failures
2. **API Connectivity**: Ensure the connector can reach Marketo's API
3. **Fallback Behavior**: The connector will fall back to static schema on API errors

### Field Type Mismatches

If data types seem incorrect:

1. **Verify in Marketo**: Check the field type definition in Marketo Admin
2. **Custom Mapping**: Some complex field types default to string
3. **Contact Support**: Report any persistent type mapping issues

## Technical Details

### API Endpoints Used
- `GET /rest/v1/leads/describe.json` - Field discovery
- Standard bulk export endpoints - Data extraction

### Implementation Files
- `source_marketo/source.py` - Main implementation
- `Leads` class - Dynamic schema generation
- `stream_fields` property - Field discovery

### Error Handling
- Graceful fallback to static schema on API failures
- Warning logs for field discovery issues
- Maintains sync reliability even with API problems

## Migration Guide

### Existing Connections
- **No action required** - existing connections will automatically benefit from custom fields support
- **Schema refresh recommended** - refresh your connection to see all available fields

### New Connections
- Custom fields will be automatically discovered during initial setup
- All available fields will be included in the default sync

## Support

For issues or questions about custom fields support:

1. Check Airbyte logs for field discovery warnings
2. Verify Marketo API permissions and field visibility
3. Contact Airbyte support with specific error messages

---

**Note**: This feature requires the updated Marketo connector with dynamic schema support. Ensure you're using the latest version of the connector for full custom fields functionality.
