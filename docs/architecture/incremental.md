# Incremental Sync

## Overview

Airbyte supports syncing data in **Incremental Append** mode i.e: syncing only replicate _new_ or _modified_ data. This prevents re-fetching data that you have already replicated from a source.

In this flavor of incremental, records in the warehouse destination will never be deleted or mutated. A copy of each new or updated record is _appended_ to the data in the warehouse. This means you can find multiple copies of the same record in the destination warehouse. We provide an "at least once" guarantee of replicating each record that is present when the sync runs.

## Definitions

A `cursor` is the value used to track whether a record should be replicated in an incremental sync. A common example of a `cursor` would be a timestamp from an `updated_at` column in a database table.

A `cursor field` is the _field_ or _column_ in the data where that cursor can be found. Extending the above example, the `updated_at` column in the database would be the `cursor field`, while the `cursor` is the actual timestamp _value_ used to determine if a record should be replicated.

We will refer to the set of records that the source identifies as being new or updated as a `delta`.

## Rules

As mentioned above, the delta from a sync will be _appended_ to the existing data in the data warehouse. Incremental will never delete or mutate existing records. Let's walk through a few examples.

### Newly Created Record

Assume that `updated_at` is our `cursor_field`. Let's say the following data already exists into our data warehouse.

```javascript
[
    { "name": "Louis XVI", "deceased": false, "updated_at":  1754 },
    { "name": "Marie Antoinette", "deceased": false, "updated_at":  1755 }
]
```

In the next sync, the delta contains the following record:

```javascript
    { "name": "Louis XVII", "deceased": false, "updated_at": 1785 }
```

At the end of this incremental sync, the data warehouse would now contain:

```javascript
[
    { "name": "Louis XVI", "deceased": false, "updated_at":  1754 },
    { "name": "Marie Antoinette", "deceased": false, "updated_at":  1755 },
    { "name": "Louis XVII", "deceased": false, "updated_at": 1785 }
]
```

### Updating a Record

Let's assume that our warehouse contains all the data that it did at the end of the previous section. Now unfortunately the king and queen lose their heads. Let's see that delta:

```javascript
[
    { "name": "Louis XVI", "deceased": true, "updated_at": 1793 },
    { "name": "Marie Antoinette", "deceased": true, "updated_at": 1793 }
]
```

The output we expect to see in the warehouse is as follows:

```javascript
[
    { "name": "Louis XVI", "deceased": false, "updated_at":  1754 },
    { "name": "Marie Antoinette", "deceased": false, "updated_at":  1755 },
    { "name": "Louis XVII", "deceased": false, "updated_at": 1785 },
    { "name": "Louis XVI", "deceased": true, "updated_at": 1793 },
    { "name": "Marie Antoinette", "deceased": true, "updated_at": 1793 }
]
```

## Source-Defined Cursor

Some sources are able to determine the cursor that they use without any user input. For example, in the [exchange rates source](../integrations/sources/exchangeratesapi-io.md), the source knows that the date field should be used to determine the last record that was synced. In these cases, simply select the incremental option in the UI.

![](../.gitbook/assets/incremental_source_defined.png)

\(You can find a more technical details about the configuration data model [here](catalog.md)\).

## User-Defined Cursor

Some sources cannot define the cursor without user input. For example, in the [postgres source](../integrations/sources/postgres.md), the user needs to choose which column in a database table they want to use as the `cursor field`. In these cases, select the column in the sync settings dropdown that should be used as the `cursor field`.

![](../.gitbook/assets/incremental_user_defined.png)

\(You can find a more technical details about the configuration data model [here](catalog.md)\).

## Getting the Latest Snapshot of data

As demonstrated in the examples above, with **Incremental Append,** a record which was updated in the source will be appended to the destination rather than updated in-place. This means that if data in the source uses a primary key \(e.g: `user_id` in the `users` table\), then the destination will end up having multiple records with the same primary key value.

However, some use cases require only the latest snapshot of the data. If you want the latest snapshot and are syncing to a destination that supports views, we recommend creating a view on your data which groups by the primary key and deduplicates by the largest `_airbyte_emitted_at` values. The `_airbyte_emitted_at` column is added by Airbyte to all records synced to the destination.

As an example, if you are syncing to a Postgres DB the `employees` table which, after a few syncs, has the following records:

| `id` | `airbyte_emitted_at` | `age` |
| :--- | :--- | :--- |
| 1 | 1000 | 25 |
| 2 | 1000 | 45 |
| 1 | 2000 | 26 |
| 3 | 2000 | 76 |

The below query is one example of how to deduplicate records sharing a primary key using the `airbyte_emitted_at` column:

```sql
CREATE VIEW latest_employees_snapshot as (
    SELECT * WHERE airbyte_emitted_at=max_emitted_at FROM (
        SELECT *, MAX(airbyte_emitted_at) OVER (PARTITION BY id) as max_emitted_at FROM employees
    ) 
);
```

You can find more relevant SQL transformations you might need to do on your data in the [Connecting EL with T using SQL \(part 1/2\)](../tutorials/connecting-el-with-t-using-sql.md#simple-sql-query)

Note that in **Incremental Append**, the size of the data in your warehouse increases monotonically since an updated record in the source is appended to the destination rather than updated in-place. If you only care about having the latest snapshot of your data, you may want to periodically run cleanup jobs which retain only the latest instance of each record, deduping by primary key.

## Known Limitations

When the source's schema changes, for example, when a column is added, renamed or deleted to an existing stream, the current behavior of **Incremental Append** is not able to handle such events yet. Therefore, it is recommended to trigger a [full refresh](full-refresh.md) to recreate at the destination the data with the new metadata included.

