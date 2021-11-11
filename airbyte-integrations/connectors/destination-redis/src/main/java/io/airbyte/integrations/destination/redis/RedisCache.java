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

  private static final String DATA_KEY = JavaBaseConstants.COLUMN_NAME_DATA;

  private static final String EMITTED_KEY = JavaBaseConstants.COLUMN_NAME_EMITTED_AT;

  private final Jedis jedis;

  public RedisCache(RedisConfig redisConfig) {
    this.jedis = RedisPoolManager.initConnection(redisConfig);
  }

  public void insert(String key, String data) {
    var index = jedis.incr(key);
    var indexKey = generateIndexKey(key, index);
    jedis.hmset(indexKey, Map.of(DATA_KEY, data, EMITTED_KEY, String.valueOf(Instant.now().toEpochMilli())));
  }

  public void rename(String key, String newkey) {
    jedis.keys(key + PATTERN).forEach(k -> {
      var index = jedis.incr(newkey);
      jedis.rename(k, generateIndexKey(newkey, index));
    });
  }

  public void delete(String keyPrefix) {
    jedis.keys(keyPrefix + PATTERN).forEach(jedis::del);
    // reset index?
  }

  public List<RedisRecord> getAll(String keyPrefix) {
    return jedis.keys(keyPrefix + PATTERN).stream()
        .map(k -> Tuple.of(k, jedis.hgetAll(k)))
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
        Long.parseLong(key.substring(key.lastIndexOf(":") + 1)),
        value.get(DATA_KEY),
        Instant.ofEpochMilli(Long.parseLong(value.get(EMITTED_KEY)))
    );
  }

}
