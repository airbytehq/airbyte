# Incremental Sync - Append

## Overview

Airbyte supports syncing data in **Incremental Append** mode i.e: syncing only replicate _new_ or _modified_ data. This prevents re-fetching data that you have already replicated from a source. If the sync is running for the first time, it is equivalent to a [Full Refresh](full-refresh-append.md) since all data will be considered as _new_.

In this flavor of incremental, records in the warehouse destination will never be deleted or mutated. A copy of each new or updated record is _appended_ to the data in the warehouse. This means you can find multiple copies of the same record in the destination warehouse. We provide an "at least once" guarantee of replicating each record that is present when the sync runs.

## Definitions

A `cursor` is the value used to track whether a record should be replicated in an incremental sync. A common example of a `cursor` would be a timestamp from an `updated_at` column in a database table.

A `cursor field` is the _field_ or _column_ in the data where that cursor can be found. Extending the above example, the `updated_at` column in the database would be the `cursor field`, while the `cursor` is the actual timestamp _value_ used to determine if a record should be replicated.

We will refer to the set of records that the source identifies as being new or updated as a `delta`.

## Rules

As mentioned above, the delta from a sync will be _appended_ to the existing data in the data warehouse. Incremental will never delete or mutate existing records. Let's walk through a few examples.

### Newly Created Record

Assume that `updated_at` is our `cursor_field`. Let's say the following data already exists into our data warehouse.

| name             | deceased | updated_at |
| :--------------- | :------- | :--------- |
| Louis XVI        | false    | 1754       |
| Marie Antoinette | false    | 1755       |

In the next sync, the delta contains the following record:

| name       | deceased | updated_at |
| :--------- | :------- | :--------- |
| Louis XVII | false    | 1785       |

At the end of this incremental sync, the data warehouse would now contain:

| name             | deceased | updated_at |
| :--------------- | :------- | :--------- |
| Louis XVI        | false    | 1754       |
| Marie Antoinette | false    | 1755       |
| Louis XVII       | false    | 1785       |

### Updating a Record

Let's assume that our warehouse contains all the data that it did at the end of the previous section. Now, unfortunately the king and queen lose their heads. Let's see that delta:

| name             | deceased | updated_at |
| :--------------- | :------- | :--------- |
| Louis XVI        | true     | 1793       |
| Marie Antoinette | true     | 1793       |

The output we expect to see in the warehouse is as follows:

| name             | deceased | updated_at |
| :--------------- | :------- | :--------- |
| Louis XVI        | false    | 1754       |
| Marie Antoinette | false    | 1755       |
| Louis XVII       | false    | 1785       |
| Louis XVI        | true     | 1793       |
| Marie Antoinette | true     | 1793       |

## Source-Defined Cursor

Some sources are able to determine the cursor that they use without any user input. For example, in the [exchange rates source](../../integrations/sources/exchange-rates.md), the source knows that the date field should be used to determine the last record that was synced. In these cases, simply select the incremental option in the UI.

![](../../.gitbook/assets/incremental_source_defined.png)

\(You can find a more technical details about the configuration data model [here](../airbyte-protocol.md#catalog)\).

## User-Defined Cursor

Some sources cannot define the cursor without user input. For example, in the [postgres source](../../integrations/sources/postgres.md), the user needs to choose which column in a database table they want to use as the `cursor field`. In these cases, select the column in the sync settings dropdown that should be used as the `cursor field`.

![](../../.gitbook/assets/incremental_user_defined.png)

\(You can find a more technical details about the configuration data model [here](../airbyte-protocol.md#catalog)\).

## Getting the Latest Snapshot of data

As demonstrated in the examples above, with **Incremental Append,** a record which was updated in the source will be appended to the destination rather than updated in-place. This means that if data in the source uses a primary key \(e.g: `user_id` in the `users` table\), then the destination will end up having multiple records with the same primary key value.

However, some use cases require only the latest snapshot of the data. This is available by using other flavors of sync modes such as [Incremental - Deduped History](incremental-deduped-history.md) instead.

Note that in **Incremental Append**, the size of the data in your warehouse increases monotonically since an updated record in the source is appended to the destination rather than updated in-place.

If you only care about having the latest snapshot of your data, you may want to look at other sync modes that will keep smaller copies of the replicated data or you can periodically run cleanup jobs which retain only the latest instance of each record.

## Inclusive Cursors

When replicating data incrementally, Airbyte provides an at-least-once delivery guarantee. This means that it is acceptable for sources to re-send some data when ran incrementally. One case where this is particularly relevant is when a source's cursor is not very granular. For example, if a cursor field has the granularity of a day \(but not hours, seconds, etc\), then if that source is run twice in the same day, there is no way for the source to know which records that are that date were already replicated earlier that day. By convention, sources should prefer resending data if the cursor field is ambiguous.

Additionally, you may run into behavior where you see the same row being emitted during each sync. This will occur if your data has not changed and you attempt to run additional syncs, as the cursor field will always be greater than or equal to itself, causing it to pull the latest row multiple times until there is new data at the source.

## Known Limitations

Due to the use of a cursor column, if modifications to the underlying records are made without properly updating the cursor field, then the updated records won't be picked up by the **Incremental** sync as expected since the source connectors extract delta rows using a SQL query looking like:

```sql
SELECT * FROM table WHERE cursor_field >= 'last_sync_max_cursor_field_value'
```

Let's say the following data already exists into our data warehouse.

| name             | deceased | updated_at |
| :--------------- | :------- | :--------- |
| Louis XVI        | false    | 1754       |
| Marie Antoinette | false    | 1755       |

At the start of the next sync, the source data contains the following new record:

| name      | deceased | updated_at |
| :-------- | :------- | :--------- |
| Louis XVI | true     | 1754       |

At the end of the second incremental sync, the data warehouse would still contain data from the first sync because the delta record did not provide a valid value for the cursor field \(the cursor field is not greater than last sync's max value, `1754 < 1755`\), so it is not emitted by the source as a new or modified record.

| name             | deceased | updated_at |
| :--------------- | :------- | :--------- |
| Louis XVI        | false    | 1754       |
| Marie Antoinette | false    | 1755       |

Similarly, if multiple modifications are made during the same day to the same records. If the frequency of the sync is not granular enough \(for example, set for every 24h\), then intermediate modifications to the data are not going to be detected and emitted. Only the state of data at the time the sync runs will be reflected in the destination.

Those concerns could be solved by using a different incremental approach based on binary logs, Write-Ahead-Logs \(WAL\), or also called [Change Data Capture \(CDC\)](../cdc.md).

The current behavior of **Incremental** is not able to handle source schema changes yet, for example, when a column is added, renamed or deleted from an existing table etc. It is recommended to trigger a [Full refresh - Overwrite](full-refresh-overwrite.md) to correctly replicate the data to the destination with the new schema changes.

If you are not satisfied with how transformations are applied on top of the appended data, you can find more relevant SQL transformations you might need to do on your data in the [Connecting EL with T using SQL \(part 1/2\)](incremental-append.md)

## Related information

- [Explore Airbyte’s incremental data synchronization](https://airbyte.com/tutorials/incremental-data-synchronization).
- [An overview of Airbyte’s replication modes](https://airbyte.com/blog/understanding-data-replication-modes).
