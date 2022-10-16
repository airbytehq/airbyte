/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class RedisNameTransformerTest {

  private RedisNameTransformer redisNameTransformer;

  @BeforeEach
  void setup() {
    this.redisNameTransformer = new RedisNameTransformer();
  }

  @Test
  void testKeyName() {
    var keyName = redisNameTransformer.keyName("namespace", "stream");
    assertThat(keyName).isEqualTo("namespace:stream");

  }

  @Test
  void testTmpKeyName() {
    var tmpKeyName = redisNameTransformer.tmpKeyName("namespace", "stream");
    assertThat(tmpKeyName).isEqualTo("tmp:namespace:stream");
  }

}
