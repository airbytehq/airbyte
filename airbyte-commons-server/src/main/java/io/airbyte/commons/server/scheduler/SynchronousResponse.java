/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.scheduler;

import io.airbyte.commons.temporal.TemporalResponse;
import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.JobConfig.ConfigType;
import java.util.Objects;
import java.util.UUID;
import javax.annotation.Nullable;

public class SynchronousResponse<T> {

  private final T output;
  private final SynchronousJobMetadata metadata;

  public static <T> SynchronousResponse<T> error(final SynchronousJobMetadata metadata) {
    return new SynchronousResponse<>(null, metadata);
  }

  public static <T> SynchronousResponse<T> success(final T output, final SynchronousJobMetadata metadata) {
    return new SynchronousResponse<>(output, metadata);
  }

  public static <T, U> SynchronousResponse<T> fromTemporalResponse(final TemporalResponse<U> temporalResponse,
                                                                   @Nullable final ConnectorJobOutput jobOutput,
                                                                   @Nullable final T responseOutput,
                                                                   final UUID id,
                                                                   final ConfigType configType,
                                                                   final UUID configId,
                                                                   final long createdAt,
                                                                   final long endedAt) {

    final SynchronousJobMetadata metadata = SynchronousJobMetadata.fromJobMetadata(
        temporalResponse.getMetadata(),
        id,
        configType,
        configId,
        jobOutput != null ? jobOutput.getConnectorConfigurationUpdated() : false,
        createdAt,
        endedAt);
    return new SynchronousResponse<>(responseOutput, metadata);
  }

  public SynchronousResponse(final T output, final SynchronousJobMetadata metadata) {
    this.output = output;
    this.metadata = metadata;
  }

  public boolean isSuccess() {
    return metadata.isSucceeded();
  }

  public T getOutput() {
    return output;
  }

  public SynchronousJobMetadata getMetadata() {
    return metadata;
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    final SynchronousResponse<?> that = (SynchronousResponse<?>) o;
    return Objects.equals(output, that.output) && Objects.equals(metadata, that.metadata);
  }

  @Override
  public int hashCode() {
    return Objects.hash(output, metadata);
  }

  @Override
  public String toString() {
    return "SynchronousResponse{" +
        "output=" + output +
        ", metadata=" + metadata +
        '}';
  }

}
