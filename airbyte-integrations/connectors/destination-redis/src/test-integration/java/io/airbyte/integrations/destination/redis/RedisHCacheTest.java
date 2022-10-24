/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import static org.assertj.core.api.Assertions.assertThat;

import java.time.Instant;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class RedisHCacheTest {

  private static RedisContainerInitializr.RedisContainer redisContainer;

  private RedisCache redisCache;

  @BeforeAll
  static void setup() {
    redisContainer = RedisContainerInitializr.initContainer();
  }

  @BeforeEach
  void init() {
    var jsonConfig = RedisDataFactory.jsonConfig(
        redisContainer.getHost(),
        redisContainer.getFirstMappedPort());
    redisCache = new RedisHCache(jsonConfig);
  }

  @AfterEach
  void clean() {
    redisCache.flushAll();
  }

  @Test
  void testInsert() {
    var key = "test_key_insert";
    // given
    redisCache.insert(key, Instant.now(), "{\"property\":\"data1\"}");
    redisCache.insert(key, Instant.now(), "{\"property\":\"data2\"}");
    redisCache.insert(key, Instant.now(), "{\"property\":\"data3\"}");

    // when
    var redisRecords = redisCache.getAll(key);

    // then
    assertThat(redisRecords)
        .isNotNull()
        .hasSize(3)
        .anyMatch(r -> r.getData().equals("{\"property\":\"data1\"}"))
        .anyMatch(r -> r.getData().equals("{\"property\":\"data2\"}"))
        .anyMatch(r -> r.getData().equals("{\"property\":\"data3\"}"));
  }

  @Test
  void testCopyWithoutReplace() {
    var key1 = "test_key_copy1";
    var key2 = "test_key_copy2";
    // given
    redisCache.insert(key1, Instant.now(), "{\"property\":\"data1\"}");
    redisCache.insert(key1, Instant.now(), "{\"property\":\"data2\"}");
    redisCache.insert(key2, Instant.now(), "{\"property\":\"data3\"}");
    redisCache.insert(key2, Instant.now(), "{\"property\":\"data4\"}");

    // when
    redisCache.copy(key1, key2, false);
    var redisRecords = redisCache.getAll(key2);

    // then
    assertThat(redisRecords)
        .isNotNull()
        .hasSize(4)
        .anyMatch(r -> r.getData().equals("{\"property\":\"data1\"}"))
        .anyMatch(r -> r.getData().equals("{\"property\":\"data2\"}"))
        .anyMatch(r -> r.getData().equals("{\"property\":\"data3\"}"))
        .anyMatch(r -> r.getData().equals("{\"property\":\"data4\"}"));
  }

  @Test
  void testCopyWithReplace() {
    var key1 = "test_key_copy_replace1";
    var key2 = "test_key_copy_replace2";
    // given
    redisCache.insert(key1, Instant.now(), "{\"property\":\"data1\"}");
    redisCache.insert(key1, Instant.now(), "{\"property\":\"data2\"}");
    redisCache.insert(key2, Instant.now(), "{\"property\":\"data3\"}");
    redisCache.insert(key2, Instant.now(), "{\"property\":\"data4\"}");

    // when
    redisCache.copy(key1, key2, true);
    var redisRecords = redisCache.getAll(key2);

    // then
    assertThat(redisRecords)
        .isNotNull()
        .hasSize(2)
        .anyMatch(r -> r.getData().equals("{\"property\":\"data1\"}"))
        .anyMatch(r -> r.getData().equals("{\"property\":\"data2\"}"));
  }

  @Test
  void testDelete() {
    var key = "test_key_delete";
    // given
    redisCache.insert(key, Instant.now(), "{\"property\":\"data1\"}");
    redisCache.insert(key, Instant.now(), "{\"property\":\"data2\"}");

    // when
    redisCache.delete(key);
    var redisRecords = redisCache.getAll(key);

    // then
    assertThat(redisRecords).isEmpty();
  }

}
