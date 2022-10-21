/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import com.fasterxml.jackson.databind.JsonNode;
import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
class RedisConfig {

  private final String host;

  private final int port;

  private final String username;

  private final String password;

  private final boolean ssl;

  private final RedisCache.CacheType cacheType;

  public RedisConfig(JsonNode jsonConfig) {
    this.host = jsonConfig.get("host").asText();
    this.port = jsonConfig.get("port").asInt(6379);
    this.username = jsonConfig.get("username").asText();
    this.password = jsonConfig.get("password").asText();
    var type = jsonConfig.get("cache_type").asText();
    this.cacheType = RedisCache.CacheType.valueOf(type.toUpperCase());
    this.ssl = jsonConfig.has("ssl") && jsonConfig.get("ssl").asBoolean();
  }

  @Override
  public String toString() {
    return "RedisConfig{" +
        "host='" + host + '\'' +
        ", port=" + port +
        ", username='" + username + '\'' +
        ", cacheType=" + cacheType +
        '}';
  }

}
