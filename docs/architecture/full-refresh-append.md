# Full Refresh - Append Sync

This readme describes Airbyte conventions around the "full refresh - Append" concept.

On the nth sync of a full refresh connection:

## Add new data to the same table. Do not touch existing data.

data in the destination _before_ the nth sync:

| Languages |
| :--- |
| Python |
| Java |

new data:

| Languages |
| :--- |
| Python |
| Java |
| Ruby |

data in the destination _after_ the nth sync:

| Languages |
| :--- |
| Python |
| Java |
| Python |
| Java |
| Ruby |

This could be useful when we are interested to know about deletion of data in the source.
This is possible if we also consider the date, or the batch id from which the data was written to the destination:

new data at the n+1th sync:

| Languages |
| :--- |
| Python |
| Ruby |

data in the destination _after_ the n+1th sync:

| Languages | batch id |
| :--- | :--- |
| Python | 1 |
| Java | 1 |
| Python | 2 |
| Java | 2 |
| Ruby | 2 |
| Python | 3 |
| Ruby | 3 |

## In the future

We will consider making a better detection of deletions in the source, especially with `Incremental`, and `Change Data Capture` based sync modes for example.
