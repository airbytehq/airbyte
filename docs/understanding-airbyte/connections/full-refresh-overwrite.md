# Full Refresh - Overwrite

## Overview

The **Full Refresh** modes are the simplest methods that Airbyte uses to sync data, as they always retrieve all available information requested from the source, regardless of whether it has been synced before. This contrasts with [**Incremental sync**](incremental-append.md), which does not sync data that has already been synced before.

In the **Overwrite** variant, new syncs will destroy all data in the existing destination table and then pull the new data in. Therefore, data that has been removed from the source after an old sync will be deleted in the destination table.

## Example Behavior

On the nth sync of a full refresh connection:

## _Replace_ existing data with new data. The connection does not create any new tables.

data in the destination _before_ the sync:

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

data in the destination _after_ the sync:

| Languages |
| :--- |
| Python |
| Java |
| Ruby |

Note: This is how Singer target-bigquery does it.

## In the future

We will consider making other flavors of full refresh configurable as first-class citizens in Airbyte. e.g. On new data, copy old data to a new table with a timestamp, and then replace the original table with the new data. As always, we will focus on adding these options in such a way that the behavior of each connector is both well documented and predictable.

## Related information

- [An overview of Airbyte’s replication modes](https://airbyte.com/blog/understanding-data-replication-modes).
- [Explore Airbyte's full refresh data synchronization](https://airbyte.com/tutorials/full-data-synchronization).
