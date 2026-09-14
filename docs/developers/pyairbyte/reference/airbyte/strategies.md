---
id: airbyte-strategies
title: airbyte.strategies
---

Module airbyte.strategies
=========================
Read and write strategies for PyAirbyte.

Classes
-------

`WriteMethod(*args, **kwds)`
:   Write methods for PyAirbyte.
    
    Unlike write strategies, write methods are expected to be fully resolved and do not require any
    additional logic to determine the best method to use.
    
    If a destination does not support the declared method, it will raise an exception.

    ### Ancestors (in MRO)

    * builtins.str
    * enum.Enum

    ### Class variables

    `APPEND`
    :   Append new records to existing records.

    `MERGE`
    :   Merge new records with existing records.
        
        This requires a primary key to be set on the stream.
        If no primary key is set, this will raise an exception.
        
        To apply this strategy in cases where some destination streams don't have a primary key,
        please use the `auto` strategy instead.

    `REPLACE`
    :   Replace existing records with new records.

    ### Instance variables

    `destination_sync_mode: DestinationSyncMode`
    :   Convert the write method to a destination sync mode.

`WriteStrategy(*args, **kwds)`
:   Read strategies for PyAirbyte.
    
    Read strategies set a preferred method for writing data to a destination. The actual method used
    may differ based on the capabilities of the destination.
    
    If a destination does not support the preferred method, it will fall back to the next best
    method.

    ### Ancestors (in MRO)

    * builtins.str
    * enum.Enum

    ### Class variables

    `APPEND`
    :   Append new records to existing records.

    `AUTO`
    :   Automatically determine the best strategy to use.
        
        This will use the following logic:
        - If there's a primary key, use merge.
        - Else, if there's an incremental key, use append.
        - Else, use full replace (table swap).

    `MERGE`
    :   Merge new records with existing records.
        
        This requires a primary key to be set on the stream.
        If no primary key is set, this will raise an exception.
        
        To apply this strategy in cases where some destination streams don't have a primary key,
        please use the `auto` strategy instead.

    `REPLACE`
    :   Replace existing records with new records.