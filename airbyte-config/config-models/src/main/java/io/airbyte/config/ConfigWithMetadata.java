/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config;

import java.time.Instant;
import java.util.Objects;

@SuppressWarnings("PMD.ShortVariable")
public class ConfigWithMetadata<T> {

  private final String configId;
  private final String configType;
  private final Instant createdAt;
  private final Instant updatedAt;
  private final T config;

  public ConfigWithMetadata(final String configId, final String configType, final Instant createdAt, final Instant updatedAt, final T config) {
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

  @Override
  public boolean equals(final Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    final ConfigWithMetadata<?> that = (ConfigWithMetadata<?>) o;
    return Objects.equals(configId, that.configId) && Objects.equals(configType, that.configType) && Objects.equals(
        createdAt, that.createdAt) && Objects.equals(updatedAt, that.updatedAt) && Objects.equals(config, that.config);
  }

  @Override
  public int hashCode() {
    return Objects.hash(configId, configType, createdAt, updatedAt, config);
  }

}
