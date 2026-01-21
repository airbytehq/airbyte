# Entity cache for search

The Entity Cache stores your connected source data in Airbyte-managed storage. Enabling the entity cache allows AI agents to make object-based queries on your data, based on your natural language prompts. When enabled, Airbyte stores data from your agent connectors and makes it available for agentic search queries.

## Why and when to use the entity cache

You should use the entity cache if you _don't_ configure your own object storage.

Some APIs have search endpoints, but many don't. This makes search operations resource-intensive. Imagine prompts like these:

- `List all customers closing this month with deal sizes greater than $5000.`
- `Search all dresses and find the ones with a color option of red.`

Even though they're short, they're complex enough to require your agent to do significant work. This can cause a variety of effects:

- Unbounded growth of the context window
- Long-running queries
- Needing to iteratively collect paginated lists of records
- API rate limiting

The result is a query that takes substantial time and resources to process, a degraded experience, and inflated costs. Enabling the entity cache gives you a way to search your datasets using data that's available to Airbyte through object storage.

## How it works

When you enable the Entity Cache:

- **Storage begins automatically**. Airbyte copies a subset of data from your agent connectors to Airbyte-managed storage. Not all data goes into the entity cache. Airbyte selects a subset of your data that it considers relevant to search actions.

- **Search becomes available**. Data from the cache is available via the search action in direct connectors.

Each connected source maintains its own isolated data store. Your data is only accessible to AI agents within your organization.

## Enable the entity cache

To enable the entity cache, follow these steps.

1. In Airbyte's Agent Engine, click Connectors.

2. Enable **Cache connected source data for agentic search**.

You can't use the entity cache until Airbyte completes its first full data population. This takes time to complete, according to the volume of data in your connected sources. You can continue using Airbyte while it populates the entity cache.

## Sync frequency

Data refreshes hourly. You can't configure the refresh rate, but you can turn off the entity cache if you need to.

## Which connectors use the cache

All agent connectors can use the entity cache. Limited, temporary exceptions to this rule are possible, however.

## Disable the entity cache

To turn off the entity cache, follow these steps.

1. In Airbyte's Agent Engine, click Connectors.

2. Disable **Cache connected source data for agentic search**.

When you turn off the cache, Airbyte removes the cached data from Airbyte storage. AI agents will no longer be able to run search actions on the cache until you re-enable the cache and data syncs again.
