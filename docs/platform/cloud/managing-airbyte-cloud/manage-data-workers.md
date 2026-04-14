---
products: cloud-plus
---

# Data worker capacity

If you are on a capacity-based plan such as Plus or Pro, Airbyte uses data workers to power your sync pipelines. Your plan includes a set number of data workers, and your cost depends on how many pipelines you run in parallel rather than the volume of data you move.

This page explains how data workers determine your sync capacity, how to monitor your usage, and how on-demand capacity can help you handle spikes.

## How data workers determine capacity

A data worker is a dedicated unit of compute that runs your connections. Each data worker can handle multiple concurrent connections, depending on the connector type:

- **API connections**: One data worker handles up to 5 concurrent API connections.
- **Database and file connections**: One data worker handles up to 2 concurrent database or file connections.

Airbyte calculates the number of data workers you need at any given moment with the following formula:

```text
Workers used = (concurrent API connections / 5) + (concurrent database connections / 2)
```

For example, if you have 10 API connections and 4 database connections running at the same time, your usage is:

```text
(10 / 5) + (4 / 2) = 2 + 2 = 4 workers
```

### What counts as each type

- **API connections** include any connection where the source is a SaaS API, such as Salesforce, HubSpot, Stripe, or GitHub.
- **Database connections** include any connection where the source is a relational database, such as PostgreSQL, MySQL, or Microsoft SQL Server (MSSQL).
- **File connections** such as S3, Google Cloud Storage (GCS), or SSH File Transfer Protocol (SFTP) count as database connections for capacity purposes.

### What happens when you reach your limit

When all of your contracted data workers are in use, Airbyte queues new syncs until a worker becomes available. Queued syncs start automatically as running syncs finish and free up capacity.

If you frequently hit your limit and don't want syncs to wait in the queue, you can reschedule connections to reduce peak concurrency, purchase additional data workers, or enable on-demand capacity for critical connections.

## On-demand capacity

On-demand capacity ensures that specific connections always run immediately, even when all your contracted data workers are in use. When you enable on-demand capacity for a connection, Airbyte uses temporary burst capacity to run the sync instead of placing it in the queue. The connection only consumes credits when no contracted capacity is available.

### How on-demand capacity works

1. When a sync starts for a connection with on-demand capacity enabled, Airbyte first checks whether contracted workers are available.
2. If contracted capacity is available, the sync runs normally at no extra cost.
3. If all contracted workers are busy, the sync runs immediately on burst capacity and consumes credits for the duration.

This means on-demand connections are never queued. They always start when scheduled.

### Identify on-demand connections

Connections that use on-demand capacity display an orange **Burst** tag in the connections list. Hover over the tag to see a message confirming that the connection uses on-demand capacity for syncs.

You can also filter the connections list to show only on-demand connections by selecting the **Burst** option in the tag filter dropdown.

### When to use on-demand capacity

On-demand capacity is useful for connections that must always run on time, such as:

- **Business-critical syncs** where delays could impact downstream dashboards or reports.
- **Time-sensitive pipelines** that feed operational systems requiring fresh data.
- **Connections with tight service-level agreements** where queuing isn't acceptable.

For connections that can tolerate occasional delays, relying on your contracted data workers and the sync queue is more cost-effective.

## Monitor data worker usage

To view data worker usage, you need the **Organization Admin** role.

### Open the usage chart

From the navigation bar, click **Organization settings** > **Usage**.

### How to interpret the chart

The chart shows daily maximum concurrent data worker usage across all workspaces in a region over a selected time period. Each bar represents one day. The chart stacks workspaces so you can see which workspace uses the most data workers each day.

![Page showing a region, a period of time, and a bar chart with maximum daily data worker usage within that period of time and region](assets/data-worker-usage.png)

Hover on a day to see a detailed breakdown.

### Filter the chart

- To change the region, click the region dropdown in the chart's upper left corner and choose a different region.
- To change the date range, click the date dropdown in the chart's upper right corner and choose a new date range.

## Optimize data worker usage

If you regularly approach your data worker limit, try rescheduling connections to reduce peak concurrency before purchasing additional workers.

- **If your usage has peaks and valleys**, find connections that run on busy days and move them to lower-usage days.

- **If your usage looks consistently high**, examine your scheduling patterns within a day. If many connections start at the same time, data worker usage spikes.

    - Stagger start times over a longer period to allow some connections to finish before others begin.

    - Avoid starting all your syncs at the top of the hour. Starting them at :15, :30, and :45 distributes work more evenly.

    - If many connections run overnight, data workers might look fully utilized while sitting unused during daylight hours.

- **If sandbox or staging workspaces consume too much capacity**, consider reducing the sync frequency in less critical workspaces.

## Buy more data workers

If you've optimized your scheduling and still need more capacity, contact your Airbyte representative or [talk to sales](https://www.airbyte.com/talk-to-sales).
