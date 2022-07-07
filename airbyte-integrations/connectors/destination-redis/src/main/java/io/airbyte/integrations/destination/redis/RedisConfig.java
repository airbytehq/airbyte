/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import com.fasterxml.jackson.databind.JsonNode;

class RedisConfig {

  private final String host;

  private final int port;

  private final String username;

  private final String password;

  private final RedisCache.CacheType cacheType;

  public RedisConfig(JsonNode jsonNode) {
    this.host = jsonNode.get("host").asText();
    this.port = jsonNode.get("port").asInt(6379);
    this.username = jsonNode.get("username").asText();
    this.password = jsonNode.get("password").asText();
    var type = jsonNode.get("cache_type").asText();
    this.cacheType = RedisCache.CacheType.valueOf(type.toUpperCase());
  }

  public RedisConfig(String host, int port, String username, String password, RedisCache.CacheType cacheType) {
    this.host = host;
    this.port = port;
    this.username = username;
    this.password = password;
    this.cacheType = cacheType;
  }

  public String getHost() {
    return host;
  }

  public int getPort() {
    return port;
  }

  public String getUsername() {
    return username;
  }

  public String getPassword() {
    return password;
  }

  public RedisCache.CacheType getCacheType() {
    return cacheType;
  }

  @Override
  public String toString() {
    return "RedisConfig{" +
        "host='" + host + '\'' +
        ", port=" + port +
        ", username='" + username + '\'' +
        ", password='" + password + '\'' +
        ", cacheType=" + cacheType +
        '}';
  }

}
