/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import redis.clients.jedis.Jedis;

class RedisPoolManager {

  private RedisPoolManager() {

  }

  static Jedis initConnection(RedisConfig redisConfig) {
    Jedis jedis = null;
    try {
      jedis = new Jedis(redisConfig.getHost(), redisConfig.getPort());
      jedis.auth(redisConfig.getUsername(), redisConfig.getPassword());
      return jedis;
    } catch (Exception e) {
      if (jedis != null) {
        jedis.close();
      }
      throw e;
    }
  }

}
