# Entity cache for search

The Entity Cache stores your connected source data in Airbyte-managed storage, enabling AI agents to search your data using natural language. When enabled, data from your agent connectors is automatically synced and made available for agentic search queries.

This feature is useful when:

- You want AI agents to search across your connected data without making live API calls
- The source system's API doesn't support the search queries you need
- You want faster, more reliable search responses

## How it works

When you enable the Entity Cache:

- **Initial sync runs automatically**. Data from your agent connectors syncs to Airbyte-managed storage when you enable the cache
- **Search becomes available**. Once the initial sync completes, AI agents can query your data
- **Manual syncs keep data fresh**. Trigger additional syncs as needed to update your cached data

Each connected source maintains its own isolated data store. Your data is only accessible to AI agents within your organization.

## Enable the entity cache

To enable the entity cache, follow these steps.

1. In Airbyte's Agent Engine, click Connectors.

2. Enable **Cache connected source data for agentic search**.

Data must complete its first sync before the cache becomes operational. The setup process takes time to complete, according to the volume of data in your connected sources. You can continue using Airbyte while the cache is being configured.

## Sync frequency

When you enable the Entity Cache, an initial sync runs automatically. After the initial sync completes, subsequent syncs must be triggered manually. Automatic scheduled syncs are not currently available for the Entity Cache.

## Which connectors use the cache

All agent connectors support the Entity Cache. You can identify connector capabilities by the badges displayed on each connector card in the Agent Engine UI:

- **Direct badge only**: The connector supports the Entity Cache for AI-powered search. Data replication to your own destination is not available.
- **Direct and Replication badges**: The connector supports both the Entity Cache and data replication. You can use both features together.

When you enable the Entity Cache, all connectors with a Direct badge will sync their data to the cache.

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

### The cache toggle is not visible

The **Cache connected source data for agentic search** toggle only appears for organizations with agent connectors configured. If you don't see this toggle, verify that you have at least one agent connector set up.

### Data seems stale

Verify the last sync completed successfully. If your data is out of date, trigger a manual sync to refresh the cache.
