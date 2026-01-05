---
sidebar_label: strategies
title: airbyte.strategies
---

Read and write strategies for PyAirbyte.

## annotations

## Enum

## DestinationSyncMode

#### \_MERGE

#### \_REPLACE

#### \_APPEND

#### \_AUTO

## WriteStrategy Objects

```python
class WriteStrategy(str, Enum)
```

Read strategies for PyAirbyte.

Read strategies set a preferred method for writing data to a destination. The actual method used
may differ based on the capabilities of the destination.

If a destination does not support the preferred method, it will fall back to the next best
method.

#### MERGE

Merge new records with existing records.

This requires a primary key to be set on the stream.
If no primary key is set, this will raise an exception.

To apply this strategy in cases where some destination streams don&#x27;t have a primary key,
please use the `auto` strategy instead.

#### APPEND

Append new records to existing records.

#### REPLACE

Replace existing records with new records.

#### AUTO

Automatically determine the best strategy to use.

This will use the following logic:
- If there&#x27;s a primary key, use merge.
- Else, if there&#x27;s an incremental key, use append.
- Else, use full replace (table swap).

## WriteMethod Objects

```python
class WriteMethod(str, Enum)
```

Write methods for PyAirbyte.

Unlike write strategies, write methods are expected to be fully resolved and do not require any
additional logic to determine the best method to use.

If a destination does not support the declared method, it will raise an exception.

#### MERGE

Merge new records with existing records.

This requires a primary key to be set on the stream.
If no primary key is set, this will raise an exception.

To apply this strategy in cases where some destination streams don&#x27;t have a primary key,
please use the `auto` strategy instead.

#### APPEND

Append new records to existing records.

#### REPLACE

Replace existing records with new records.

#### destination\_sync\_mode

```python
@property
def destination_sync_mode() -> DestinationSyncMode
```

Convert the write method to a destination sync mode.

