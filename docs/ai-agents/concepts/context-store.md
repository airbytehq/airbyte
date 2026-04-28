---
sidebar_position: 2
---

# Context Store

The Context Store is a managed, searchable replica of select entities from all your connected data sources. Airbyte populates it from the connectors in your workspace and gives agents a fast, consistent way to search your business data in natural language, without hitting the underlying APIs for every request.

Some third-party APIs have search endpoints, but many don't. Without the Context Store, prompts like these force your agent to list, page through, and filter records from the API in real time:

- `List all customers closing this month with deal sizes greater than $5000.`
- `Search all dresses and find the ones with a color option of red.`

Working this way causes a variety of problems:

- Unbounded growth of the context window
- Long-running queries
- Iterative collection of paginated lists of records
- API rate limiting

The result is a query that takes substantial time and resources to process, a degraded experience, and inflated costs.

The Context Store solves this problem by making key fields available to your agents in Airbyte-managed storage. When you turn it on, Airbyte replicates a curated subset of the entities in your agent connectors into the store and keeps it up to date. Agents then answer these kinds of questions with fast, indexed searches instead of live API crawls.

## What's in the Context Store

Each connected source has its own isolated store. Airbyte curates the store for search, not archival.

- Airbyte selects a subset of fields and entities that are useful for search, not every record or field in the source.
- Each organization's data is only accessible to agents within that organization.
- Data in the store refreshes on a schedule that depends on your plan. See [Billing and pricing](../admin/billing) for details.

For the list of entities each connector contributes, see [Agent connectors](../connectors).

## Who can configure the Context Store

The Context Store is an organization-level setting. Only organization administrators see the **Manage Context Store** button and can turn the store on or off. End users who run Chats and Automations see the benefits of the store but don't configure it.

## Turn on the Context Store

1. In the Airbyte Agents web app, click **Credentials** in the left sidebar.

2. At the top of the Credentials page, click **Manage Context Store**.

3. In the slide-out, turn on **Enable Context Store**.

When you turn on the Context Store:

- **Storage begins automatically.** Airbyte starts copying data from each agent connector in your workspace into the store.
- **Search becomes available.** As soon as a connector has enough data, its entities are available to agents through the search action.

You can continue using Airbyte while the store populates. First-time population takes longer for connectors with large datasets.

## Check Context Store status

You can check Context Store status in two places on the **Credentials** page: per connector and per entity.

### Per-connector status

Each credential in the Credentials list shows a status badge when the Context Store is on for its workspace.

- **Ready.** The store is populated and fully available for search.
- **Preview.** The first population is still in progress, but some data is already searchable.
- **Building Preview.** The first population is in progress and no data is searchable yet.
- **Loading.** Airbyte is preparing the store for this connector.

Ready and Preview are both usable states for agents. Preview means newer records may still be arriving.

### Per-entity status

Click the status badge on a credential to open a detailed view for that connector. The view lists every entity Airbyte populates for the connector, along with:

- **Entity.** The entity name, for example `contacts`, `deals`, or `products`.
- **Status.** `Ready`, `Preview`, `Building Preview`, `Initializing`, or `Updating`.
- **Records.** The number of records currently searchable for that entity.
- **Last Synced** or **Last Updated.** The most recent time Airbyte refreshed that entity.

Use this view to confirm which entities are ready to query and which are still populating.

## Turn off the Context Store

1. In the Airbyte Agents web app, click **Credentials** in the left sidebar.

2. At the top of the Credentials page, click **Manage Context Store**.

3. In the slide-out, turn off **Enable Context Store**.

When you turn off the Context Store, Airbyte removes the replicated data from the store. Agents can no longer use the search action until you turn the store back on and Airbyte repopulates it.

## How agents use the Context Store

When an agent processes a prompt, it chooses between two execution paths for each connector operation:

- **Context Store search.** The agent queries the pre-indexed replica in the Context Store. This path handles filtering, sorting, and aggregation without calling the third-party API, so it returns results faster and uses fewer tokens. Agents prefer this path when the entity is available in the Context Store.
- **Direct request.** The agent calls the third-party API in real time. This path always returns the most current data, and it's the only option for entities that aren't in the Context Store or for write operations like creating and updating records.

Agents choose between these paths automatically. You don't need to specify which path to use in your prompts. In chat, each tool call displays a badge that indicates whether it used the Context Store or a direct request.

## How search works

The Context Store supports structured search with filter operators, field selection, sorting, and cursor-based pagination. Agents translate natural-language prompts into structured queries automatically, so most users don't need to construct queries by hand.

If you build agents with the SDK or API, you can call `context_store_search` directly and pass structured filters. For details on the query model, see the [SDK reference](../reference/sdk/airbyte_agent_sdk) and individual [connector reference pages](../connectors).

## Initial backfill

When the Context Store populates data for a connector, Airbyte runs an initial backfill. Backfill time depends on the amount of data and third-party API rate limits, and can range from minutes to days.

During the backfill, Airbyte makes data available to agents progressively. You don't have to wait for the backfill to finish before agents can search. An entity in **Preview** status already has partial data that agents can query. As the backfill continues, more records become searchable until the entity reaches **Ready** status.

The per-entity detail view on the Credentials page shows record counts and timestamps so you can track backfill progress.

## When to use the Context Store

Turn the Context Store on when:

- You want agents to search across large amounts of connector data with predictable latency.
- You want prompts like "find all X where Y" to run as a single search instead of a live API crawl.
- You want consistent search behavior across connectors, including connectors whose APIs don't offer their own search endpoint.

You may want to skip the Context Store when:

- You already maintain your own copy of the relevant data and prefer to expose it through your own tools.
- You only need to read or write a small number of records at a time and don't need to search across a dataset.

## Limitations

- All agent connectors and interfaces can use the Context Store and always try to do so unless you turn it off.
- Turning the Context Store off and on again triggers a fresh population. Repopulating can take a long time if your system contains substantial amounts of data. Plan for this if you rely on search-heavy prompts.
