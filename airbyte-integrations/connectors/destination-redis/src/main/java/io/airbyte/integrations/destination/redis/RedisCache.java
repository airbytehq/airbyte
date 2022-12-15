/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.Closeable;
import java.time.Instant;
import java.util.List;

/**
 * Interface defined to support caching in different Redis data types for different purposes.
 */
public interface RedisCache extends Closeable {

  ObjectMapper objectMapper = new ObjectMapper()
      .findAndRegisterModules();

  /**
   * Return implementation cache type.
   *
   */
  CacheType cacheType();

  /**
   * Insert data in the implementing Redis cache type.
   *
   * @param key to insert data in
   * @param timestamp of the data
   * @param data to be inserted
   */
  void insert(String key, Instant timestamp, String data);

  /**
   * Copy data from one key to another with the option to replace.
   *
   * @param sourceKey key to copy data from
   * @param destinationKey key to copy data to
   * @param replace flag indicating whether the previous data should be deleted
   */
  void copy(String sourceKey, String destinationKey, boolean replace);

  /**
   * Delete all data with the provided key.
   *
   * @param key to delete data for
   */
  void delete(String key);

  /**
   * Retrieve all data with the provided key.
   *
   * @param key for which to retrieve data
   * @return List of RedisRecords for the provided key.
   */
  List<RedisRecord> getAll(String key);

  /**
   * Ping the Redis cache for a healthcheck status.
   *
   * @param message to send with the healthcheck
   */
  void ping(String message);

  /**
   * Remove all keys with the related data from all existing databases
   */
  void flushAll();

  /**
   * Close all underlying resource for the Redis cache.
   */
  @Override
  void close();

  enum CacheType {
    HASH
  }

}
