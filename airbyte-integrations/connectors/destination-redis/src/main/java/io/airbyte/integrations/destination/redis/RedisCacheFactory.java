/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.redis.RedisCache.CacheType;

public class RedisCacheFactory {

  private RedisCacheFactory() {

  }

  static RedisCache newInstance(JsonNode jsonConfig) {
    CacheType cacheType = CacheType.valueOf(jsonConfig.get("cache_type").asText().toUpperCase());
    return switch (cacheType) {
      case HASH -> new RedisHCache(jsonConfig);
    };
  }

}
