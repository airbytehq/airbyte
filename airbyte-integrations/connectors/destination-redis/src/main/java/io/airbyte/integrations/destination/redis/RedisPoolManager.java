/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import redis.clients.jedis.Jedis;

class RedisPoolManager {

  private static final int CONNECTION_TIMEOUT = 10000;

  private RedisPoolManager() {

  }

  static Jedis initConnection(RedisConfig redisConfig) {
    Jedis jedis = null;
    try {
      if (redisConfig.isSsl()) {
        jedis = new Jedis(redisConfig.getHost() ,redisConfig.getPort(), CONNECTION_TIMEOUT,  true);
      } else {
        jedis = new Jedis(redisConfig.getHost() ,redisConfig.getPort() ,CONNECTION_TIMEOUT,  false);
        jedis.auth(redisConfig.getUsername(), redisConfig.getPassword());
      }
      return jedis;
    } catch (Exception e) {
      if (jedis != null) {
        jedis.close();
      }
      throw new RuntimeException(e);
    }
  }

}
