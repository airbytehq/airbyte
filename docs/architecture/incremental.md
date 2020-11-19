# Incremental

## Overview

Incremental syncs in Airbyte allow sources to replicate only new or modified data. This prevents re-sending data that has already been sent to your warehouse. We will call this set of new or updated records the delta going forward.

## Configuration
A stream that is using incremental sync must specify a `cursor_field`. This is the field that Airbyte will use to determine if a record should be included in the delta of the current sync. In other words, it tells Airbyte whether this record is new or has been modified. Some sources may specify a `default_cursor_field`, which specifies which field the author thought should be used to determining if a record should be included in the delta. The user can choose to use that default or specify their own.

## Rules
The delta from a sync will be _appended_ to the existing data in the data warehouse. Incremental will never delete or mutate existing records. Let's walk through a few examples.

### Newly Created Record

Assume that `updated_at` is our `cursor_field`. Let's say the following data already exists into our data warehouse.
```json
[
    { "name": "Louis XVI", "deceased": false, "updated_at":  1754 },
    { "name": "Marie Antoinette", "deceased": false, "updated_at":  1755 }
]
```

In the next sync the delta contains the following record:
```json
    { "name": "Louis XVII", "deceased": false, "updated_at": 1785 }
```

At the end of this incremental sync the data warehouse would now contain:
```json
[
    { "name": "Louis XVI", "deceased": false, "updated_at":  1754 },
    { "name": "Marie Antoinette", "deceased": false, "updated_at":  1755 },
    { "name": "Louis XVII", "deceased": false, "updated_at": 1785 }
]
```

### Updating a Record
Let's assume that our warehouse contains all of the data that it did at the end of the previous section. Now unfortunately the king and queen lose their heads. Let's see that delta:
```json
[
    { "name": "Louis XVI", "deceased": true, "updated_at": 1793 },
    { "name": "Marie Antoinette", "deceased": true, "updated_at": 1793 }
]
```

The output we expect to see in the warehouse is as follows.
```json
[
    { "name": "Louis XVI", "deceased": false, "updated_at":  1754 },
    { "name": "Marie Antoinette", "deceased": false, "updated_at":  1755 },
    { "name": "Louis XVII", "deceased": false, "updated_at": 1785 },
    { "name": "Louis XVI", "deceased": true, "updated_at": 1793 },
    { "name": "Marie Antoinette", "deceased": true, "updated_at": 1793 }
]
```

### Schema Migration
If the schema for the stream changes, Airbyte will _not_ allow an incremental sync to that stream. The user must first run a full refresh.
