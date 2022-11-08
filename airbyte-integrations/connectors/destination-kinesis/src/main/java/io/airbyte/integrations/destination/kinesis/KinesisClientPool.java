/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kinesis;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import software.amazon.awssdk.services.kinesis.KinesisClient;

/**
 * KinesisClientPool class for managing a pool of kinesis clients with different configurations.
 */
public class KinesisClientPool {

  private static final ConcurrentHashMap<KinesisConfig, Tuple<KinesisClient, AtomicInteger>> clients;

  static {
    clients = new ConcurrentHashMap<>();
  }

  private KinesisClientPool() {

  }

  /**
   * Initializes a Kinesis client for accessing Kinesis. If there is already an existing client with
   * the provided configuration it will return the existing one and increase the usage count, if not
   * it will return a new one.
   *
   * @param kinesisConfig used to configure the Kinesis client.
   * @return KinesisClient which can be used to access Kinesis.
   */
  public static KinesisClient initClient(KinesisConfig kinesisConfig) {
    var cachedClient = clients.get(kinesisConfig);
    if (cachedClient != null) {
      cachedClient.value2().incrementAndGet();
      return cachedClient.value1();
    } else {
      var client = KinesisUtils.buildKinesisClient(kinesisConfig);
      clients.put(kinesisConfig, Tuple.of(client, new AtomicInteger(1)));
      return client;
    }
  }

  /**
   * Returns a Kinesis client to the pool. If the client is no longer used by any other external
   * instances it will be closed and removed from the map, if not only its usage count will be
   * decreased.
   *
   * @param kinesisConfig that was used to configure the Kinesis client.
   */
  public static void closeClient(KinesisConfig kinesisConfig) {
    var cachedClient = clients.get(kinesisConfig);
    if (cachedClient == null) {
      throw new IllegalStateException("No session for the provided config");
    }
    int count = cachedClient.value2().decrementAndGet();
    if (count < 1) {
      cachedClient.value1().close();
      clients.remove(kinesisConfig);
    }
  }

}
