/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import com.fasterxml.jackson.databind.JsonNode;
import redis.clients.jedis.Jedis;

class RedisPoolManager {

  private static final String PARAM_HOST = "host";
  private static final String PARAM_PORT = "port";
  private static final String PARAM_USERNAME = "username";
  private static final String PARAM_PASSWORD = "password";
  private static final String PARAM_SSL_MODE = "ssl_mode";
  private static final int CONNECTION_TIMEOUT = 10000;

  static Jedis initConnection(JsonNode jsonConfig) {
    Jedis jedis = null;
    final String host = jsonConfig.get(PARAM_HOST).asText();
    final int port = jsonConfig.get(PARAM_PORT).asInt(6379);
    final String username = jsonConfig.has(PARAM_USERNAME) ? jsonConfig.get(PARAM_USERNAME).asText() : "";
    final String password = jsonConfig.has(PARAM_PASSWORD) ? jsonConfig.get(PARAM_PASSWORD).asText() : "";
    try {
      if (RedisSslUtil.isSsl(jsonConfig)) {
        RedisSslUtil.setupCertificates(jsonConfig.get(PARAM_SSL_MODE));
        jedis = new Jedis(host, port, CONNECTION_TIMEOUT, true);
      } else {
        jedis = new Jedis(host, port, CONNECTION_TIMEOUT, false);
      }
      jedis.auth(username, password);
      return jedis;
    } catch (Exception e) {
      if (jedis != null) {
        jedis.close();
      }
      throw new RuntimeException(e);
    }
  }

}
