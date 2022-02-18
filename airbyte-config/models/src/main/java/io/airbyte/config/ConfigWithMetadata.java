/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config;

import java.time.Instant;

public class ConfigWithMetadata<T> {

  private final String configId;
  private final String configType;
  private final Instant createdAt;
  private final Instant updatedAt;
  private final T config;

  public ConfigWithMetadata(String configId, String configType, Instant createdAt, Instant updatedAt, T config) {
    this.configId = configId;
    this.configType = configType;
    this.createdAt = createdAt;
    this.updatedAt = updatedAt;
    this.config = config;
  }

  public String getConfigId() {
    return configId;
  }

  public String getConfigType() {
    return configType;
  }

  public Instant getCreatedAt() {
    return createdAt;
  }

  public Instant getUpdatedAt() {
    return updatedAt;
  }

  public T getConfig() {
    return config;
  }

}
