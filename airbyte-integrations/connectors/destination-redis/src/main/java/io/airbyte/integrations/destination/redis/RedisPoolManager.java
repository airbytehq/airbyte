package io.airbyte.integrations.destination.redis;

import redis.clients.jedis.Jedis;

/*
* Pool Manager for keeping track of opened pools and connections.
* */
class RedisPoolManager {


    private RedisPoolManager() {

    }

    static Jedis initConnection(RedisConfig redisConfig) {
        return new Jedis(redisConfig.getHost(), redisConfig.getPort());
    }

    static void closeConnection() {

        // close connection

        // close pool when all connections have been released

    }

}
