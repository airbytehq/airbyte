# Incremental Sync

## Overview

Incremental syncs in Airbyte allow sources to replicate only new or modified data. This prevents re-fetching data that you have already replicated from a source. We will call this set of new or updated records the delta going forward.

## Configuration

For a source to do incremental sync is must be able to keep track of new and updated records. This can take a couple different forms. Before we jump into them, we are going to use the word cursor or cursor field to describe the field or column in the data that the Connector uses to determine if any given record is new or has been updated since the last sync. A commonly used cursor is the "updated_at" field in a database table. 

## Source-Defined Cursor

Some sources are able to determine the cursor that the use without any user input. For example, in the exchange rates api source, the source itself can determine that the `date` field should be used to determine the last record that was synced. In these cases, the source will set the `cursor_field` attribute in the `AirbyteStream`.

## User-Defined Cursor

Some sources cannot define the cursor without user input. For example, in the postgres source, the user needs to tell the connector which column (e.g: `updated_at`) in the selected tables should be used to find the delta. The author of the source cannot predict this. In these cases the user sets the `cursor_field` in the `ConfiguredAirbyteStream`.

In some cases, the source may propose a `default_cursor_field` in the `AirbyteStream`. In this case, if the user does not specify a `cursor_field` in the `ConfiguredAirbyteStream`, Airbyte will fallback on the default provided by the source. The user is allowed to override the source's `default_cursor_field` by setting the `cursor_field` value in the `ConfiguredAirbyteStream`, but they CANNOT override the `cursor_field` specified in an `AirbyteStream`

## Rules

The delta from a sync will be _appended_ to the existing data in the data warehouse. Incremental will never delete or mutate existing records. Let's walk through a few examples.

### Newly Created Record

Assume that `updated_at` is our `cursor_field`. Let's say the following data already exists into our data warehouse.

```javascript
[
    { "name": "Louis XVI", "deceased": false, "updated_at":  1754 },
    { "name": "Marie Antoinette", "deceased": false, "updated_at":  1755 }
]
```

In the next sync the delta contains the following record:

```javascript
    { "name": "Louis XVII", "deceased": false, "updated_at": 1785 }
```

At the end of this incremental sync the data warehouse would now contain:

```javascript
[
    { "name": "Louis XVI", "deceased": false, "updated_at":  1754 },
    { "name": "Marie Antoinette", "deceased": false, "updated_at":  1755 },
    { "name": "Louis XVII", "deceased": false, "updated_at": 1785 }
]
```

### Updating a Record

Let's assume that our warehouse contains all of the data that it did at the end of the previous section. Now unfortunately the king and queen lose their heads. Let's see that delta:

```javascript
[
    { "name": "Louis XVI", "deceased": true, "updated_at": 1793 },
    { "name": "Marie Antoinette", "deceased": true, "updated_at": 1793 }
]
```

The output we expect to see in the warehouse is as follows.

```javascript
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

