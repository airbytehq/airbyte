# Redis Destination

Redis is an open source (BSD licensed), in-memory data structure store, used as a database, cache, pub/sub and message broker. 
Redis provides data structures such as strings, hashes, lists, sets, sorted sets with range queries, bitmaps, hyperloglogs, geospatial indexes, and streams. 
Redis has built-in replication, Lua scripting, LRU eviction, transactions, and different levels of on-disk persistence.
To achieve top performance, Redis works with an in-memory dataset. Depending on your use case, you can persist your data either by periodically dumping the dataset to disk or by appending each command to a disk-based log. You can also disable persistence if you just need a feature-rich, networked, in-memory cache.
[Read more about Redis](https://redis.io/)


This connector maps an incoming Airbyte namespace and stream to a different key in the Redis data structure. The connector supports the `append` sync mode by
adding keys to an existing keyset and `overwrite` by deleting the existing ones and replacing them with the new ones.

The implementation uses the [Jedis](https://github.com/redis/jedis) java client to access the Redis cache. [RedisCache](./src/main/java/io/airbyte/integrations/destination/redis/RedisCache.java) is the main entrypoint for defining operations that can be performed against Redis.
The interface allows you to implement any Redis supported data type for storing data based on your needs.
At the moment there is only one implementation [RedisHCache](./src/main/java/io/airbyte/integrations/destination/redis/RedisHCache.java) which stores the incoming messages in a Hash structure. Internally it uses a Jedis instance retrieved from the 
[RedisPoolManager](./src/main/java/io/airbyte/integrations/destination/redis/RedisPoolManager.java). Retrieve records from the Redis cache are mapped to [RedisRecord](./src/main/java/io/airbyte/integrations/destination/redis/RedisRecord.java)

The [RedisMessageConsumer](./src/main/java/io/airbyte/integrations/destination/redis/RedisMessageConsumer.java)
class contains the logic for handling airbyte messages and storing them in Redis.

## Development

See the [RedisHCache](./src/main/java/io/airbyte/integrations/destination/redis/RedisHCache.java) class for an example on how to use the Jedis client for accessing the Redis cache.

If you want to learn more, read the [Jedis docs](https://github.com/redis/jedis/wiki)