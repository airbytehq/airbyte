/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import com.fasterxml.jackson.databind.JsonNode;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import redis.clients.jedis.Jedis;

public class RedisHCache implements RedisCache {

  private static final String PATTERN = ":[0-9]*";

  private final Jedis jedis;

  public RedisHCache(JsonNode jsonConfig) {
    this.jedis = RedisPoolManager.initConnection(jsonConfig);
  }

  @Override
  public CacheType cacheType() {
    return CacheType.HASH;
  }

  @Override
  public void insert(String key, Instant timestamp, String data) {
    var index = jedis.incr(key);
    var indexKey = generateIndexKey(key, index);
    var hash = Map.of(
        RedisRecord.ID_PROPERTY, String.valueOf(index),
        RedisRecord.DATA_PROPERTY, data,
        RedisRecord.TIMESTAMP_PROPERTY, String.valueOf(timestamp.toEpochMilli()));
    jedis.hmset(indexKey, hash);
  }

  @Override
  public void copy(String sourceKey, String destinationKey, boolean replace) {
    if (replace) {
      delete(destinationKey);
    }
    jedis.keys(sourceKey + PATTERN).forEach(k -> {
      var index = jedis.incr(destinationKey);
      jedis.rename(k, generateIndexKey(destinationKey, index));
    });
  }

  @Override
  public void delete(String key) {
    jedis.keys(key + PATTERN).forEach(jedis::del);
  }

  @Override
  public List<RedisRecord> getAll(String key) {
    return jedis.keys(key + PATTERN).stream()
        .map(jedis::hgetAll)
        .map(h -> objectMapper.convertValue(h, RedisRecord.class))
        .collect(Collectors.toList());
  }

  @Override
  public void ping(String message) {
    jedis.ping(message);
  }

  @Override
  public void flushAll() {
    jedis.flushAll();
  }

  @Override
  public void close() {
    jedis.close();
  }

  private String generateIndexKey(String key, Long id) {
    return key + ":" + id;
  }

}
