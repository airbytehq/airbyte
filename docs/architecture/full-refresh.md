# Full Refresh

This readme describes Airbyte conventions around the "full refresh" concept. Out in the world, there are many ways to define this term. We want the behavior of Airbyte connectors to be predictable, so we are adopting a preferred definition. This readme also describes what behavior to fall back on if the preferred convention cannot be used.

On the nth sync of a full refresh connection:

## PREFERRED: _Replace_ existing data with new data. The connection does not create any new tables.

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

## FALLBACK: Add new data to a new table. Do not touch existing data.

data in the destination _before_ the sync:

| Languages\_\ |
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

| Languages\_\ |
| :--- |
| Python |
| Java |

| Languages\_\ |
| :--- |
| Python |
| Java |
| Ruby |

Note: This is how Singer target-csv, target-postgres does it.

## In Practice

Not all data warehouses will necessarily be able to adhere to either of these conventions. Given this convention, here is how implementing full refresh should be handled:

* If the destination supports our _preferred_ definition of full refresh, use it. No extra documentation required as this is what users should expect as the default full refresh behavior. 
* If it does not, then use the _fallback_ definition. Document exactly what the output format of the data will be as this will not meet the default expectation of an Airbyte user.
* If that destination does not support either of these definitions, document the actual behavior. Keep in mind this will break all of the expectations of an Airbyte user, so be as exhaustive as possible in describing the format of the output data.

## In the future

We will consider making other flavors of full refresh configurable as first-class citizens in Airbyte. e.g. On new data, copy old data to a new table with a timestamp, and then replace the original table with the new data. As always, we will focus on adding these options in such a way that the behavior of each connector is both well documented and predictable.

