# Redis Destination

Redis is an open source (BSD licensed), in-memory data structure store, used as a database, cache, pub/sub and message broker. 
Redis provides data structures such as strings, hashes, lists, sets, sorted sets with range queries, bitmaps, hyperloglogs, geospatial indexes, and streams. 
Redis has built-in replication, Lua scripting, LRU eviction, transactions, and different levels of on-disk persistence.
To achieve top performance, Redis works with an in-memory dataset. Depending on your use case, you can persist your data either by periodically dumping the dataset to disk or by appending each command to a disk-based log. You can also disable persistence if you just need a feature-rich, networked, in-memory cache.
[Read more about Redis](https://redis.io/)


This connector maps an incoming Airbyte namespace and stream to a different key in the Redis data structure. The connector supports the `append` sync mode by
adding keys to an existing keyset and `overwrite` by deleting the existing ones and replacing them with the new ones.