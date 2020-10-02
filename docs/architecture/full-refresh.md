# Full Refresh

These are two possible definitions we could adopt for this phrase. We should choose one as the convention for how to implement destinations moving forward. While in the future, we could support both and just be explicit about their difference, for now we should pick one to focus on.

On the n<sup>th</sup> sync of a full refresh connection:

### _Replace_ existing data new data. The connection does not create any new tables. 

data in the destination _before_ the sync:

| Languages  | 
|---|
| Python  |
| Java  |

new data:

| Languages  | 
|---|
| Python  |
| Java  |
| Ruby  |

data in the destination _after_ the sync:

| Languages  | 
|---|
| Python  |
| Java  |
| Ruby  |

Note: This is how Singer target-bigquery does it.

### Add new data to a new table. Do not touch existing data.

data in the destination _before_ the sync:
    
| Languages  | 
|---|
| Python  |
| Java  |

new data:

| Languages  | 
|---|
| Python  |
| Java  |
| Ruby  |

data in the destination _after_ the sync:

| Languages_\<timestamp\>  | 
|---|
| Python  |
| Java  |

| Languages_\<new timestamp\>  | 
|---|
| Python  |
| Java  |
| Ruby  |

Note: This is how Singer target-csv, target-postgres does it.

### Caveats

Not all data warehouses will necessarily be able to adhere to both of these conventions. Once we choose the definition we prefer, someone developing a new integration should do the following:
* If the destination supports our adopted definition it, they should use it. 
* If it does not, then they should prefer the other definition and document it clearly. 
* If that destination does not support either of these definitions, then they should document to the best of the ability the custom behaviour.
