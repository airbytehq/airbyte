# Entity cache for search

The Entity Cache stores your connected source data in Airbyte-managed storage, enabling AI agents to search your data using natural language. When enabled, data from your agent connectors is automatically synced and made available for agentic search queries.

This feature is useful when:

- You want AI agents to search across your connected data without making live API calls
- The source system's API doesn't support the search queries you need
- You want faster, more reliable search responses

## How It Works

When you enable the Entity Cache:

- **Data syncs automatically**. Data from your agent connectors syncs to Airbyte-managed storage on a configurable schedule
- **Search becomes available**. Once the initial sync completes, AI agents can query your data
- **Data stays fresh**. Subsequent syncs keep your cached data up to date

Each connected source maintains its own isolated data store. Your data is only accessible to AI agents within your organization.

## Enable the entity cache

To enable the entity cache, follow these steps.

1. In Airbyte's Agent Engine, click Connectors.

2. Enable **Cache connected source data for agentic search**.

Data must complete its first sync before the cache becomes operational. The setup process takes time to complete, according to the volume of data in your connected sources. You can continue using Airbyte while the cache is being configured.

## Configure sync frequency

<!-- 
This appears to be explicitly unset for the entity cache. Need to verify if there's an automatic sync.

You can, optionally, configure how often your data syncs to the cache using a cron expression. If you don't specify a schedule, you need to manually resync data. To configure the sync schedule:

1. In Airbyte's Agent Engine, click **Data replication**.

2. Select **Airbyte Hosted Data**

3. Enter a cron expression in the Sync Schedule field. The cron expression follows Quartz cron format. When you enter an expression, the system validates it and displays a human-readable description of the schedule (e.g., "Every day at 2:00 AM"). Examples of common schedules:

    ```text
    0 0 2 * * ? - Every day at 2:00 AM
    0 0 */6 * * ? - Every 6 hours
    0 0 0 * * MON - Every Monday at midnight
    ```

Leave the field empty if you want to run syncs manually. 
-->

## Which connectors use the cache

All agent connectors that support direct data access use the entity cache if you've enabled it. These connectors are designed to work with the cache for search operations and have a `Direct` badge in the Airbyte's Agent Engine UI.

Some connectors support both the entity cache and data replication. They can replicate data to a destination and use the entity cache for AI-powered search.

You can use both features together if your connector supports it.

## Disable the Cache

To disable the entity cache, follow these steps.

1. In Airbyte's Agent Engine, click Connectors.

2. Disable **Cache connected source data for agentic search**.

When you disable the cache, the cached data is removed from Airbyte-managed storage. AI agents will no longer be able to search your data until you re-enable the cache and data syncs again.

## Troubleshooting

### My AI agent can't find data I know exists

- Verify the entity cache is enabled.
- Check that the source has completed at least one sync.
- Ensure the data you're searching for is in a stream that's being synced.

### Data seems stale

Verify the last sync completed successfully.
