/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import io.airbyte.integrations.base.JavaBaseConstants;
import java.io.Closeable;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import redis.clients.jedis.Jedis;

public class RedisCache implements Closeable {

  private static final String PATTERN = ":[0-9]*";

  private final Jedis jedis;

  public RedisCache(RedisConfig redisConfig) {
    this.jedis = RedisPoolManager.initConnection(redisConfig);
  }

  public void insert(String key, Map<String, String> data) {
    var index = jedis.incr(key);
    var indexKey = generateIndexKey(key, index);
    jedis.hmset(indexKey, data);
  }

  public void rename(String key, String newkey) {
    jedis.keys(key + PATTERN).forEach(k -> {
      var index = jedis.incr(newkey);
      jedis.rename(k, generateIndexKey(newkey, index));
    });
  }

  public void delete(String key) {
    jedis.keys(key + PATTERN).forEach(jedis::del);
    // reset index?
  }

  public List<RedisRecord> getAll(String key) {
    return jedis.keys(key + PATTERN).stream()
        .map(k -> Tuple.of(k.substring(k.lastIndexOf(":") + 1), jedis.hgetAll(k)))
        .map(this::asRedisRecord)
        .collect(Collectors.toList());
  }

  public void ping(String message) {
    jedis.ping(message);
  }

  public void flush() {
    jedis.flushAll();
  }

  @Override
  public void close() {
    jedis.close();
  }

  private String generateIndexKey(String key, Long id) {
    return key + ":" + id;
  }

  private RedisRecord asRedisRecord(Tuple<String, Map<String, String>> record) {
    var key = record.value1();
    var value = record.value2();
    return new RedisRecord(
        Long.parseLong(key),
        value.get(JavaBaseConstants.COLUMN_NAME_DATA),
        Instant.ofEpochMilli(Long.parseLong(value.get(JavaBaseConstants.COLUMN_NAME_EMITTED_AT)))
    );
  }

}
