import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Snowflake Migration Guide

## Upgrading to 4.0.0

### What changed and why

Version 4.0.0 upgrades Destination Snowflake to the [Direct-Load](/platform/using-airbyte/core-concepts/direct-load-tables) paradigm, which provides significant performance improvements and reduces warehouse compute costs compared to the previous Typing and Deduping approach.

**Key improvements:**
- **Reduced warehouse costs**: Direct-Load eliminates the expensive typing and deduping SQL queries that ran at the end of each sync, significantly reducing compute time and costs.
- **No unbounded raw table growth**: Unlike Typing and Deduping, Direct-Load does not maintain persistent raw tables that grow indefinitely, reducing storage costs.
- **Faster data loading**: The connector performs type casting during the sync rather than in a separate SQL operation, improving overall sync performance.
- **CDC soft-delete support**: A new option allows you to handle CDC deletions as soft-deletes (preserving deleted records with a timestamp) rather than hard-deletes (removing records entirely).

### Who is affected

This upgrade affects different users in different ways depending on how you interact with Snowflake tables:

#### Scenario 1: Final tables only (no action required)
If you only query the final tables (the typed, deduped tables in your configured schema) and never interact with raw tables, you can upgrade without taking any action. The structure and format of your final tables remain the same, and you'll benefit from reduced costs and improved performance.

#### Scenario 2: Raw tables only (action required)
If you only query the raw tables (in the `airbyte_internal` schema) and have the `Disable Final Tables` option enabled, you must keep this option enabled before upgrading. After upgrading, the connector will automatically enable the `Legacy raw tables` option, which maintains the raw table format you're currently using.

#### Scenario 3: Both raw and final tables (migration required)
If you query both raw and final tables, this use case is no longer supported in a single connection. You must create two separate destination connectors and run two connections in parallel:
- One connector with `Legacy raw tables` enabled (for raw table queries)
- One connector with `Legacy raw tables` disabled (for final table queries)

### Understanding Direct-Load

Direct-Load is an architectural improvement that changes how data flows from Airbyte into Snowflake:

**Previous approach (Typing and Deduping):**
1. During sync: Write JSON data to raw tables in `airbyte_internal` schema
2. At end of sync: Execute expensive SQL query to cast types and deduplicate data into final tables
3. Raw tables grow indefinitely and are never cleaned up

**New approach (Direct-Load):**
1. During sync: Connector performs type casting and writes typed data directly to final tables
2. No persistent raw tables are maintained (temporary staging tables are used during sync but deleted afterward)
3. Deduplication happens during the sync for `Append + Deduped` mode

**Key differences:**
- **Record visibility**: In `Append` mode, records appear in final tables immediately during the sync (not just at the end). In `Append + Deduped` mode, records are written to a temporary table during the sync and upserted to the final table periodically.
- **Schema evolution**: Direct-Load uses `ALTER TABLE` statements for schema changes, which may fail if historical data cannot be cast to new types. In such cases, you must either run a refresh (removing existing records) or manually update historical records.
- **Raw tables**: By default, Direct-Load does not create persistent raw tables. Enable `Legacy raw tables` if you need the old raw table format.

### CDC soft-delete feature

Version 4.0.0 introduces a new configuration option called **CDC deletion mode** with two settings:

#### Hard delete (default)
When a source record is deleted (detected via CDC), the corresponding record is permanently removed from the destination table. This is the default behavior and maintains backward compatibility with previous versions.

#### Soft delete (new option)
When a source record is deleted, the record remains in the destination table but is marked with a deletion timestamp in the `_AB_CDC_DELETED_AT` column. This allows you to:
- Preserve historical records of deleted data
- Query deleted records for audit or analysis purposes
- Filter out deleted records in your queries when needed

**Column details:**
- Column name: `_AB_CDC_DELETED_AT`
- Data type: `TIMESTAMP_TZ` (timestamp with timezone)
- Value: `NULL` for active records, timestamp of deletion for deleted records

**Filtering soft-deleted records:**
```sql
-- Exclude soft-deleted records
SELECT * FROM your_schema.your_table
WHERE _AB_CDC_DELETED_AT IS NULL;

-- Query only soft-deleted records
SELECT * FROM your_schema.your_table
WHERE _AB_CDC_DELETED_AT IS NOT NULL;

-- Include all records with deletion status
SELECT *, 
       CASE WHEN _AB_CDC_DELETED_AT IS NULL THEN 'active' ELSE 'deleted' END AS record_status
FROM your_schema.your_table;
```

**Important notes:**
- This feature only applies to sources that support CDC (Change Data Capture)
- The `_AB_CDC_DELETED_AT` column only appears in tables when the source emits CDC deletion events
- If you enable soft-deletes, you must update downstream SQL queries and dbt models to filter out deleted records where appropriate

### Raw tables vs final tables in version 4.0.0

#### Final tables (default behavior)
Final tables are the typed, deduped tables in your configured schema. In version 4.0.0, these tables have the following structure:

**Columns:**
- All columns from your stream schema (with appropriate Snowflake data types)
- `_AIRBYTE_RAW_ID`: Unique identifier for each record (UUID)
- `_AIRBYTE_GENERATION_ID`: Incremented with each refresh operation
- `_AIRBYTE_EXTRACTED_AT`: Timestamp when Airbyte extracted the record from the source
- `_AIRBYTE_LOADED_AT`: Timestamp when Airbyte loaded the record into Snowflake
- `_AIRBYTE_META`: JSON object containing sync metadata and any type validation errors
- `_AB_CDC_DELETED_AT`: (Only present if source supports CDC) Timestamp of deletion for soft-deleted records

**Behavior:**
- Records are typed according to your stream schema
- Deduplication is performed based on primary key and cursor fields (for `Append + Deduped` mode)
- Schema evolution is handled via `ALTER TABLE` statements
- No persistent raw tables are maintained

#### Legacy raw tables (opt-in via configuration)
If you enable the `Legacy raw tables` option, the connector writes data in the old raw table format:

**Location:** `airbyte_internal` schema (or custom schema specified in `Airbyte Internal Table Dataset Name`)

**Columns:**
- `_airbyte_raw_id`: Unique identifier (UUID)
- `_airbyte_generation_id`: Generation counter
- `_airbyte_extracted_at`: Extraction timestamp
- `_airbyte_loaded_at`: Load timestamp
- `_airbyte_meta`: Metadata JSON object
- `_airbyte_data`: JSON blob containing the entire record

**Behavior:**
- All data stored as JSON in `_airbyte_data` column
- No typing or deduplication performed
- No final tables are created
- Compatible with pre-4.0.0 raw table format

### Step-by-step migration instructions

#### For users who only query final tables

**Pre-upgrade checklist:**
1. Verify that you do not have any queries, dashboards, or dbt models that reference raw tables in the `airbyte_internal` schema
2. Ensure your Snowflake user has necessary permissions (no changes required from previous versions)
3. Take note of current record counts in your final tables for post-upgrade verification

**Upgrade steps:**
1. In Airbyte UI, navigate to your Snowflake destination
2. Click "Upgrade" when prompted for version 4.0.0
3. No configuration changes are required
4. Run your connections to start syncing with the new version

**Post-upgrade verification:**
1. Verify record counts match expected values:
   ```sql
   SELECT COUNT(*) FROM your_schema.your_table;
   ```
2. Check that new records are appearing correctly
3. Verify that metadata columns are populated:
   ```sql
   SELECT _AIRBYTE_RAW_ID, _AIRBYTE_EXTRACTED_AT, _AIRBYTE_LOADED_AT, _AIRBYTE_META
   FROM your_schema.your_table
   LIMIT 10;
   ```
4. Monitor your Snowflake warehouse costs - you should see a reduction in compute time for Airbyte syncs

**Expected changes:**
- Reduced warehouse compute costs (no more typing and deduping queries)
- Faster sync completion times
- No changes to final table structure or data
- Error messages in `_airbyte_meta` will show `DESTINATION_SERIALIZATION_ERROR` instead of `DESTINATION_TYPECAST_ERROR` (this should not affect recommended query patterns)

#### For users who only query raw tables

**Pre-upgrade checklist:**
1. Verify that the `Disable Final Tables` option is currently enabled in your destination configuration
2. Document all queries, dashboards, and dbt models that reference raw tables
3. Take note of current record counts in your raw tables

**Upgrade steps:**
1. **Before upgrading**, ensure `Disable Final Tables` is enabled in your destination configuration
2. In Airbyte UI, navigate to your Snowflake destination
3. Click "Upgrade" when prompted for version 4.0.0
4. After upgrading, verify that the `Legacy raw tables` option is automatically enabled
5. Run your connections to start syncing with the new version

**Post-upgrade verification:**
1. Verify that raw tables are still being written to `airbyte_internal` schema:
   ```sql
   SELECT COUNT(*) FROM airbyte_internal.your_stream_name;
   ```
2. Check that the raw table structure remains unchanged:
   ```sql
   DESCRIBE TABLE airbyte_internal.your_stream_name;
   ```
3. Verify that `_airbyte_data` column contains JSON data as expected:
   ```sql
   SELECT _airbyte_raw_id, _airbyte_data
   FROM airbyte_internal.your_stream_name
   LIMIT 10;
   ```
4. Confirm that no final tables are being created in your configured schema

**Expected changes:**
- Raw tables continue to work exactly as before
- No changes to raw table structure or data
- No final tables are created
- Warehouse costs remain similar to previous version (since you're not using typing and deduping)

#### For users who query both raw and final tables

**Pre-upgrade checklist:**
1. Identify all queries, dashboards, and dbt models that reference raw tables
2. Identify all queries, dashboards, and dbt models that reference final tables
3. Plan your dual-connector setup (see below)
4. Consider using different schemas or schema prefixes to avoid naming conflicts

**Migration approach:**

Since version 4.0.0 does not support writing both raw and final tables in a single connection, you must create two separate destination connectors:

**Connector 1: For raw tables**
1. Create a new Snowflake destination in Airbyte (or modify your existing one)
2. Enable the `Legacy raw tables` option
3. Configure to write to a dedicated schema (e.g., `raw_data_schema`)
4. Update all connections that need raw tables to use this destination

**Connector 2: For final tables**
1. Create a second Snowflake destination in Airbyte
2. Keep `Legacy raw tables` disabled (default)
3. Configure to write to your main schema (e.g., `analytics_schema`)
4. Update all connections that need final tables to use this destination

**Parallel operation:**
1. Run both connections in parallel (they can sync the same sources to different destinations)
2. Schedule both connections to run at similar times to maintain data freshness
3. Monitor both connections to ensure they're syncing successfully

**Validation period:**
1. Run both connections for at least one full sync cycle
2. Verify record counts match between raw and final tables:
   ```sql
   -- Count in raw tables
   SELECT COUNT(*) FROM raw_data_schema.your_stream_name;
   
   -- Count in final tables
   SELECT COUNT(*) FROM analytics_schema.your_stream_name;
   ```
3. Compare sample records to ensure data consistency
4. Update and test all downstream queries, dashboards, and dbt models

**Considerations:**
- Running two connections will double your sync frequency and may increase source API usage
- You'll need to manage two separate destination configurations
- Warehouse costs may increase due to running two separate syncs, but this may be offset by Direct-Load performance improvements
- Consider whether you can migrate away from raw table dependencies over time to simplify your setup

#### Enabling CDC soft-deletes

If you want to enable the new CDC soft-delete feature:

**Configuration steps:**
1. In Airbyte UI, navigate to your Snowflake destination settings
2. Find the "CDC deletion mode" option in the "Sync Behavior" section
3. Change from "Hard delete" (default) to "Soft delete"
4. Save your configuration
5. Run your connections to start syncing with soft-deletes enabled

**Post-configuration steps:**
1. Verify the `_AB_CDC_DELETED_AT` column appears in tables that receive CDC deletion events:
   ```sql
   DESCRIBE TABLE your_schema.your_table;
   ```
2. Test the soft-delete behavior by deleting a record in your source system and verifying it's marked (not removed) in Snowflake:
   ```sql
   SELECT * FROM your_schema.your_table
   WHERE _AB_CDC_DELETED_AT IS NOT NULL;
   ```
3. Update all downstream SQL queries and dbt models to filter out soft-deleted records:
   ```sql
   -- Add this WHERE clause to your queries
   WHERE _AB_CDC_DELETED_AT IS NULL
   ```

**Important notes:**
- Only enable soft-deletes if your source supports CDC and emits deletion events
- Soft-deleted records will accumulate over time, increasing storage costs
- Consider implementing a cleanup process to permanently delete old soft-deleted records if needed
- This setting applies to all streams in the connection

### Troubleshooting

#### Issue: "Schema evolution failed" error

**Cause:** Direct-Load uses `ALTER TABLE` statements for schema changes. If a column type changes and historical records cannot be cast to the new type, the schema change will fail.

**Solution:**
1. Run a refresh and choose to remove existing records (this will rebuild the table with the new schema)
2. OR manually update historical records to be compatible with the new type:
   ```sql
   -- Example: Update invalid values before schema change
   UPDATE your_schema.your_table
   SET problematic_column = NULL
   WHERE problematic_column = 'invalid_value';
   ```

#### Issue: Raw tables are missing after upgrade

**Cause:** Direct-Load does not create persistent raw tables by default.

**Solution:**
1. If you need raw tables, enable the `Legacy raw tables` option in your destination configuration
2. Run a full refresh to populate the raw tables

#### Issue: Downstream queries are returning deleted records

**Cause:** If you enabled CDC soft-deletes, deleted records remain in the table with a deletion timestamp.

**Solution:**
Update your queries to filter out soft-deleted records:
```sql
WHERE _AB_CDC_DELETED_AT IS NULL
```

#### Issue: "_AB_CDC_DELETED_AT column not found" error

**Cause:** The `_AB_CDC_DELETED_AT` column only appears in tables when:
1. The source supports CDC and emits deletion events
2. CDC soft-delete mode is enabled

**Solution:**
1. Verify your source supports CDC
2. Verify CDC soft-delete mode is enabled in your destination configuration
3. If you don't need CDC soft-deletes, use hard-delete mode (default) and don't reference this column

#### Issue: Higher warehouse costs after upgrade

**Cause:** If you're running two connections (for both raw and final tables), you may see increased costs.

**Solution:**
1. Evaluate whether you can migrate away from raw table dependencies
2. Consider consolidating to a single connection type (either raw or final tables)
3. Optimize your sync frequency if running two connections
4. Monitor costs over time - Direct-Load should reduce per-sync costs even with two connections

#### Issue: Permission errors after upgrade

**Cause:** Direct-Load may require slightly different permissions for staging operations.

**Solution:**
Ensure your Snowflake user has the following permissions:
```sql
-- Required permissions (same as before)
GRANT USAGE ON WAREHOUSE your_warehouse TO ROLE your_role;
GRANT USAGE ON DATABASE your_database TO ROLE your_role;
GRANT USAGE ON SCHEMA your_schema TO ROLE your_role;
GRANT CREATE TABLE ON SCHEMA your_schema TO ROLE your_role;
GRANT CREATE STAGE ON SCHEMA your_schema TO ROLE your_role;

-- For existing tables
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA your_schema TO ROLE your_role;
```

### Rollback plan

If you need to revert to version 3.x after upgrading:

**Important considerations:**
- Direct-Load (4.0.0) and Typing and Deduping (3.x) use different internal state formats
- Downgrading may require a full refresh to resync all data
- Final table structures should remain compatible between versions

**Rollback steps:**
1. In Airbyte UI, navigate to your Snowflake destination
2. Change the Docker image version back to 3.x (contact support if needed)
3. Keep your existing connections paused until rollback is complete
4. Test with a single connection first before enabling all connections
5. You may need to run a full refresh on affected connections to rebuild state

**Recommendation:**
- Test the upgrade in a staging environment first
- Keep a backup of your destination configuration
- Monitor the first few syncs after upgrading closely
- Have a rollback plan ready but expect that Direct-Load will work well for most use cases

### Additional resources

- [Direct-Load tables documentation](/platform/using-airbyte/core-concepts/direct-load-tables)
- [Snowflake destination documentation](/integrations/destinations/snowflake)
- [Airbyte metadata fields](/platform/understanding-airbyte/airbyte-metadata-fields)
- [Snowflake Time Travel documentation](https://docs.snowflake.com/en/user-guide/data-time-travel)
- [Snowflake ALTER TABLE documentation](https://docs.snowflake.com/en/sql-reference/sql/alter-table)

<MigrationGuide />

## Upgrading to 3.0.0

This version introduces [Destinations V2](/release_notes/upgrading_to_destinations_v2/#what-is-destinations-v2), which provides better error handling, incremental delivery of data for large syncs, and improved final table structures. To review the breaking changes, and how to upgrade, see [here](/release_notes/upgrading_to_destinations_v2/#quick-start-to-upgrading). These changes will likely require updates to downstream dbt / SQL models, which we walk through [here](/release_notes/upgrading_to_destinations_v2/#updating-downstream-transformations). Selecting `Upgrade` will upgrade **all** connections using this destination at their next sync. You can manually sync existing connections prior to the next scheduled sync to start the upgrade early.

Worthy of specific mention, this version includes:

- Per-record error handling
- Clearer table structure
- Removal of sub-tables for nested properties
- Removal of SCD tables

Learn more about what's new in Destinations V2 [here](/platform/using-airbyte/core-concepts/typing-deduping).

## Upgrading to 2.0.0

Snowflake no longer supports GCS/S3. Please migrate to the Internal Staging option. This is recommended by Snowflake and is cheaper and faster.
