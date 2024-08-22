---
products: all
---

# Full Refresh - Overwrite + Deduped

## Overview

The **Full Refresh** modes are the simplest methods that Airbyte uses to sync data, as they always retrieve all available information requested from the source, regardless of whether it has been synced before. This contrasts with [**Incremental sync**](./incremental-append.md), which does not sync data that has already been synced before.

In the **Overwrite + Deduped** variant, new syncs will replace all data in the existing destination table and then pull the new data in. Therefore, data that has been removed from the source after an old sync will be deleted in the destination table. The **deduped** variant also means that the data in the final table will be unique per primary key \(unlike [Full Refresh Overwrite](./full-refresh-overwrite.md)\). This is determined by sorting the data using the cursor field and keeping only the latest de-duplicated data row.

Full Refresh syncs may be [resumed](/understanding-airbyte/resumability) (to recover from transient errors for example), when this happens, duplicate may happen. If avoiding duplicate is a strong requirement, we recommend using **Overwrite + Deduped** over **Overwrite**. Bear in mind that deduplication incurs additional warehouse costs.

## Example Behavior

On the nth sync of a full refresh connection:

## _Replace_ existing data with new data. The connection does not create any new tables.

data in the destination _before_ the sync:

| Languages |
| :-------- |
| Python    |
| Java      |
| Bash      |

new data in the source:

| Languages |
| :-------- |
| Python    |
| Java      |
| Ruby      |

data in the destination _after_ the sync (note how the old value of "bash" is no longer present):

| Languages |
| :-------- |
| Python    |
| Java      |
| Ruby      |

## Destination-specific mechanism for full refresh

The mechanism by which a destination connector accomplishes the full refresh will vary wildly from destination to destination. For our certified database and data warehouse destinations, we will be recreating the final table each sync. This allows us leave the previous sync's data viewable by writing to a "final-table-tmp" location as the sync is running, and at the end dropping the old "final" table, and renaming the new one into place. That said, this may not possible for all destinations, and we may need to erase the existing data at the start of each full-refresh sync.

## Related information

- [An overview of Airbyte’s replication modes](https://airbyte.com/blog/understanding-data-replication-modes).
- [Explore Airbyte's full refresh data synchronization](https://airbyte.com/tutorials/full-data-synchronization).
