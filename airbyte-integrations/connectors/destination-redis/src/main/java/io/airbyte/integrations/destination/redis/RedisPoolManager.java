package io.airbyte.integrations.destination.redis;

import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;

/*
* Pool Manager for keeping track of opened pools and connections.
* */
class RedisPoolManager {


    private RedisPoolManager() {

    }

    static Jedis initConnection(RedisConfig redisConfig) {

        var jedisPool = new JedisPool(redisConfig.getHost(), redisConfig.getPort());

        return jedisPool.getResource();
    }

    static void closeConnection() {

        // close connection

        // close pool when all connections have been released

    }

}
