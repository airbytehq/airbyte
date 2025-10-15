---
products: all
---

# Resumability & Resumable Full Refresh

:::info

This page describes a coming-soon feature. Resumable Full Refresh will be available as of Airbyte v1.0.0.

:::

## Resumability

Airbyte strives to create resilient syncs that can handle many types of issues (for example, networking issues, flaky source APIs or under provisioned
destination servers). Whenever possible, Airbyte syncs are resumable. “Resumable” in this context means that if something goes wrong in the first attempt
of your sync, we will immediately try again with a subsequent attempt - in fact, Airbyte will keep retrying as long as the source is producing new records
and the destination can commit them. In order to achieve this resumability, Airbyte may deliver a record more than once - **Airbyte is a deliver at-least-once system**.

Consider a Postgres source. We could build a query that does `select * from users`, which would guarantee that each row is emitted only once, but that would lead to some problems:

- First, it would keep a long-lasting transaction lock on the `users` table for the duration of the sync.  This would slow down the source.
- Tables over a certain size would not be able to fit in memory. This would dramatically slow down the database while syncing (or even crashing) the database.
- There is no logical cursor that Airbyte can use as a placeholder to resume from if we need to retry the sync.

To get around all of these issues, we issue queries that look like this:

- `select * from users where CTID >= X AND CTID < Y`
- `select * from users where CTID >= Y AND CTID < Z`
- `...`

CTID is a special postgres column that we use to paginate the contents of the table, and this affords us a cursor we can use to break the query into chunks, both keeping the database happy, and allowing Airbyte to resume the sync half-way though if needed. However, if the sync only got partially through a query, the records in that query will be re-sent on the second attempt. If you want your destination to only contain a unique instance for each record, please choose a destination and sync mode that includes deduplication.

While this example uses a database source, the same logic holds for API sources. For instance, a series of requests to a user's API endpoint might be:

- `curl -x GET api.com/v1/users?page=1`
- `curl -x GET api.com/v1/users?page=2`
- `...`

Resumability applies to all sync modes, including standard Full Refresh + Overwrite and Full Refresh + Append syncs, along with [Refreshes](./../operator-guides/refreshes.md).

## Resumable Full Refresh

Resumability is an inherent feature of Incremental syncs. 


Although incremental syncs are superior in all cases, they require implementing a cursor, which is not always possible.

Consider a data analyst without direct access to the underlying database. Not being able to introspect schemas makes identifying and selecting the correct cursor column a challenge.
In fact, there might not be a cursor column to start! Full Refresh, in this case, is the only option.

### Artificial Cursors

Enabling Resumable Full Refresh requires **Artificial Cursors**. An Artificial Cursor is a best-effort attempt to construct a relatively stable cursor.
These cursors are artificial as they are often not present in the data schema, e.g. Postgres's CTID is a system-level column, and subject to independent
change i.e. without external control or input. This differs from a proper cursor column, e.g. an `update_at` column, that is present in the data schema,
and changes in response to user input.


### Enabling Resumable Full Refresh

Resuamble Full Refresh is automatically enabled on connections with:
1) A Resumable-Full-Refresh-enabled Source
2) A Refresh-enabled Destination

The following Database Sources support Resumable Full Refresh as of 9th July 2024:
1) **Source MySql >= 3.4.7**
   1) Tables without primary keys do not support Resumable Full Refresh.
2) **Source MsSql >= 4.0.27**
   1) Tables without primary keys do not support Resumable Full Refresh.
3) **Source Postgres >= 3.4.10**
   1) views do not support Resumable Full Refresh.
4) **Source Mongo >= 1.3.14**

The following API Sources support Resumable Full Refresh as of 9th July 2024:
1) All Sources on Python CDK version 1.1.0 and above.

### Identifying Resumed Streams

The platform emits the following log lines to help identify resumed streams:
```angular2html
2024-07-08 22:58:40 replication-orchestrator > Number of Resumed Full Refresh Streams: {1}
2024-07-08 22:58:40 replication-orchestrator >  Resumed stream name: activities namespace: null
```
