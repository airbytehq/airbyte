# Incremental

## Overview

Incremental syncs in Airbyte allow sources to replicate only new or modified data. This prevents re-sending data that has already been sent to your warehouse. We will call this set of new or updated records the delta going forward.

## Rules
The delta from a sync will be _appended_ to the existing data in the data warehouse. Incremental will never delete or mutate existing records. Let's walk through a few examples.

### Newly Created Record

Assume that you have already synced the following records into you data warehouse.
```json
[
    { "name": "Louis XVI", "deceased": false },
    { "name": "Marie Antoinette", "deceased": false }
]
```

In the next sync a the delta contains the following record:
```json
    { "name": "Louis XVII", "deceased": false }
```

At the end of this incremental sync the data warehouse would now contain:
```json
[
    { "name": "Louis XVI", "deceased": false },
    { "name": "Marie Antoinette", "deceased": false },
    { "name": "Louis XVII", "deceased": false }
]
```

### Updating a Record
Let's assume that our warehouse contains all of the data that it did at the end of the previous section. Now unfortunately the king and queen lose their heads. Let's see that delta:
```json
[
    { "name": "Louis XVI", "deceased": true },
    { "name": "Marie Antoinette", "deceased": true }
]
```

The output we expect to see in the warehouse is as follows.
```json
[
    { "name": "Louis XVI", "deceased": false },
    { "name": "Marie Antoinette", "deceased": false },
    { "name": "Louis XVII", "deceased": false },
    { "name": "Louis XVI", "deceased": true },
    { "name": "Marie Antoinette", "deceased": true }
]
```

### Schema Migration
If the schema for the stream changes, Airbyte will _not_ allow an incremental sync to that stream. The user must first run a full refresh.
