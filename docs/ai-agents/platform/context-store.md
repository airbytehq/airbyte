---
sidebar_position: 5
---

# Context store

Some APIs have search endpoints, but many don't. This makes search operations resource-intensive. Imagine prompts like these:

- `List all customers closing this month with deal sizes greater than $5000.`
- `Search all dresses and find the ones with a color option of red.`

Even though they're short, they're complex enough to require your agent to do significant work. This can cause a variety of effects:

- Unbounded growth of the context window
- Long-running queries
- Needing to iteratively collect paginated lists of records
- API rate limiting

The result is a query that takes substantial time and resources to process, a degraded experience, and inflated costs.

The context store solves this problem by making key fields available to your agents in Airbyte-managed object storage. When you enable it, the context store allows AI agents to make object-based queries on your data, based on natural language prompts. Agents can query it with less than half a second of latency.

## Enable the context store

To enable the context store, follow these steps.

1. In Airbyte's Agent Engine, click Connectors.

2. Enable **Enable Airbyte-managed Context Store for agent search**.

When you enable the context store:

- **Storage begins automatically**. Airbyte copies a subset of data from your agent connectors to Airbyte-managed storage. Not all data goes into the context store. Airbyte selects a subset of your data that it considers relevant to search actions.

- **Search becomes available**. Data from the cache is available via the search action in direct connectors.

Each connected source maintains its own isolated data store. Your data is only accessible to AI agents within your organization.

You can't use the context store until Airbyte completes its first full data population. This takes time to complete, according to the volume of data in your connected sources. You can continue using Airbyte while it populates the context store.

## Disable the context store

To turn off the context store, follow these steps.

1. In Airbyte's Agent Engine, click Connectors.

2. Disable **Cache connected source data for agentic search**.

When you turn off the cache, Airbyte removes the cached data from Airbyte storage. AI agents will no longer be able to run search actions on the cache until you re-enable the cache and data syncs again.

## Notes and limitations

- You may choose to avoid enabling the context store if you have configured your own object storage. If you already have a copy of key pieces of customer data, make this available to your agents via self-implemented tools.

- Data refreshes hourly. You can't configure the refresh rate, but you can turn off the context store if you need to.

- All agent connectors can use the context store. Limited, temporary exceptions to this rule are possible, however.
