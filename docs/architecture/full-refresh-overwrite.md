# Full Refresh - Overwrite Sync

This readme describes Airbyte conventions around the "full refresh - Overwrite" concept. 

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

