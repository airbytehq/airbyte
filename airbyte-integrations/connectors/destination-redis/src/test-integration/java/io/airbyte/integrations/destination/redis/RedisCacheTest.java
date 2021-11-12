/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;

class RedisCacheTest {

 /* private static RedisContainerInitializr.RedisContainer redisContainer;

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
    redisCache = new RedisCache(new RedisConfig(jsonConfig));
  }

  @AfterEach
  void clean() {
    redisCache.flush();
  }

  @Test
  void testInsert() {
    // given
    redisCache.insert("test_key_insert", "{\"property\":\"data1\"}");
    redisCache.insert("test_key_insert", "{\"property\":\"data2\"}");
    redisCache.insert("test_key_insert", "{\"property\":\"data3\"}");

    // when
    var redisRecords = redisCache.getAll("test_key_insert");

    // then
    assertThat(redisRecords)
        .isNotNull()
        .hasSize(3)
        .anyMatch(r -> r.getData().equals("{\"property\":\"data1\"}"))
        .anyMatch(r -> r.getData().equals("{\"property\":\"data2\"}"))
        .anyMatch(r -> r.getData().equals("{\"property\":\"data3\"}"));
  }

  @Test
  void testDelete() {

    // given
    redisCache.insert("test_key_delete", "{\"property\":\"data1\"}");
    redisCache.insert("test_key_delete", "{\"property\":\"data2\"}");

    // when
    redisCache.delete("test_key_delete");
    var redisRecords = redisCache.getAll("test_key_delete");

    // then
    assertThat(redisRecords).isEmpty();
  }

  @Test
  void testRename() {
    // given
    redisCache.insert("test_key_rename1", "{\"property\":\"data1\"}");
    redisCache.insert("test_key_rename1", "{\"property\":\"data2\"}");
    redisCache.insert("test_key_rename2", "{\"property\":\"data3\"}");
    redisCache.insert("test_key_rename2", "{\"property\":\"data4\"}");

    // when
    redisCache.rename("test_key_rename1", "test_key_rename2");
    var redisRecords = redisCache.getAll("test_key_rename2");

    // then
    assertThat(redisRecords)
        .isNotNull()
        .hasSize(4)
        .anyMatch(r -> r.getData().equals("{\"property\":\"data1\"}"))
        .anyMatch(r -> r.getData().equals("{\"property\":\"data2\"}"))
        .anyMatch(r -> r.getData().equals("{\"property\":\"data3\"}"))
        .anyMatch(r -> r.getData().equals("{\"property\":\"data4\"}"));
  }
*/
}
