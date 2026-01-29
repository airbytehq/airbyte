<!--
STUB DOCUMENTATION - DO NOT MERGE AS-IS

This README is a placeholder to document the proposed configuration and behavior
differences for source-mongodb-gen3 compared to source-mongodb-v2. Before merging:
- Either delete this file and the gen3 connector directory, OR
- Complete the full gen3 connector implementation with proper spec, code, and docs

This stub exists to facilitate discussion and planning of the gen3 rollout strategy.
-->

# MongoDB Gen3

This connector provides a cleaner configuration experience for MongoDB data replication, built on the same proven codebase as `source-mongodb-v2` but with simplified defaults that prioritize sync stability over strict schema enforcement.

## Migrating from V2

### Why Gen3?

The `source-mongodb-v2` connector evolved over time with configuration options that became tightly coupled in ways that created confusion and fragility:

1. **`schema_enforced`** controlled three distinct behaviors simultaneously:
   - Whether to sample documents for rich schema discovery
   - Whether to filter synced fields to match the discovered schema
   - Whether to wrap data in a `"data"` field or use top-level columns

2. **Default behavior was fragile**: With `schema_enforced=true` (the default), new fields appearing in MongoDB documents could cause sync issues or be silently dropped.

Gen3 decouples these concerns and provides stable defaults out of the box.

### Configuration Differences

Gen3 replaces the single `schema_enforced` boolean with two clearer options:

**V2 `schema_enforced=true` (default) migrates to:**
- `use_packed_mode: false` - Data delivered as top-level columns
- `detect_schema: true` - Rich schema discovery for downstream metadata

**V2 `schema_enforced=false` migrates to:**
- `use_packed_mode: true` - Data wrapped in a single "data" column (Fivetran-style "packed mode")
- `detect_schema: false` - Users can opt-in to rich schema detection if desired

### Behavior Differences

**Data Delivery:**
- **V2 with `schema_enforced=true`**: Fields delivered as top-level columns, but undiscovered fields could be dropped
- **V2 with `schema_enforced=false`**: All data wrapped in a single `"data"` column
- **Gen3**: All fields delivered at top-level, including fields not present in the discovered schema

**Schema Evolution:**
- **V2**: New fields in MongoDB could cause sync failures or data loss depending on configuration
- **Gen3**: New fields are automatically included in syncs without requiring schema rediscovery

**Sync Stability:**
- **V2**: Users had to choose between rich schemas (fragile) or schemaless mode (no schema metadata)
- **Gen3**: Rich schema metadata for destinations AND stable syncs that don't fail on schema changes

### Migration Steps

1. Create a new MongoDB Gen3 source connection with the same credentials
2. Configure the same database(s) and collection(s)
3. Run an initial sync to establish the new connection
4. Verify data is flowing correctly
5. Disable or delete the old V2 connection

### Rollback

If you need to revert to V2 behavior:
- Your V2 connection remains unchanged and can be re-enabled at any time
- Gen3 and V2 can run in parallel during migration
- No data migration is required - both connectors read directly from MongoDB
