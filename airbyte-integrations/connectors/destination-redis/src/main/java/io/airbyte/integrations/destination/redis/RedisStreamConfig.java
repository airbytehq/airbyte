/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import io.airbyte.protocol.models.v0.DestinationSyncMode;

public class RedisStreamConfig {

  private final String key;

  private final String tmpKey;

  private final DestinationSyncMode destinationSyncMode;

  public RedisStreamConfig(String key, String tmpKey, DestinationSyncMode destinationSyncMode) {
    this.key = key;
    this.tmpKey = tmpKey;
    this.destinationSyncMode = destinationSyncMode;
  }

  public String getKey() {
    return key;
  }

  public String getTmpKey() {
    return tmpKey;
  }

  public DestinationSyncMode getDestinationSyncMode() {
    return destinationSyncMode;
  }

  @Override
  public String toString() {
    return "RedisStreamConfig{" +
        "key='" + key + '\'' +
        ", tmpKey='" + tmpKey + '\'' +
        ", destinationSyncMode=" + destinationSyncMode +
        '}';
  }

}
