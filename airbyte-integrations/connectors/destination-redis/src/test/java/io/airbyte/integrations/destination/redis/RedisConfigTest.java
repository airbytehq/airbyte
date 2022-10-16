/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class RedisConfigTest {

  private RedisConfig redisConfig;

  @BeforeEach
  void setup() {
    var jsonNode = RedisDataFactory.jsonConfig("127.0.0.1", 6379);
    this.redisConfig = new RedisConfig(jsonNode);
  }

  @Test
  void testConfig() {
    assertThat(redisConfig)
        .hasFieldOrPropertyWithValue("username", "default")
        .hasFieldOrPropertyWithValue("password", "pw")
        .hasFieldOrPropertyWithValue("host", "127.0.0.1")
        .hasFieldOrPropertyWithValue("port", 6379)
        .hasFieldOrPropertyWithValue("cacheType", RedisCache.CacheType.HASH);

  }

}
