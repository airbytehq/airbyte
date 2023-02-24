/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config;

import java.time.Instant;
import java.util.Objects;

@SuppressWarnings("PMD.ShortVariable")
public record ConfigWithMetadata<T>(String configId, String configType, Instant createdAt, Instant updatedAt, T config) {

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

}
