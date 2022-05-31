/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.client;

import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.workers.temporal.JobMetadata;
import java.nio.file.Path;
import java.time.Instant;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

public class SynchronousJobMetadata {

  private final UUID id;
  private final ConfigType configType;
  private final UUID configId;

  private final long createdAt;
  private final long endedAt;
  private final boolean succeeded;

  private final Path logPath;

  public static SynchronousJobMetadata fromJobMetadata(final JobMetadata jobMetadata,
                                                       final UUID id,
                                                       final ConfigType configType,
                                                       final UUID configId,
                                                       final long createdAt,
                                                       final long endedAt) {
    return new SynchronousJobMetadata(
        id,
        configType,
        configId,
        createdAt,
        endedAt,
        jobMetadata.isSucceeded(),
        jobMetadata.getLogPath());
  }

  public SynchronousJobMetadata(final UUID id,
                                final ConfigType configType,
                                final UUID configId,
                                final long createdAt,
                                final long endedAt,
                                final boolean succeeded,
                                final Path logPath) {
    this.id = id;
    this.configType = configType;
    this.configId = configId;
    this.createdAt = createdAt;
    this.endedAt = endedAt;
    this.succeeded = succeeded;
    this.logPath = logPath;
  }

  public UUID getId() {
    return id;
  }

  public ConfigType getConfigType() {
    return configType;
  }

  public Optional<UUID> getConfigId() {
    return Optional.ofNullable(configId);
  }

  public long getCreatedAt() {
    return createdAt;
  }

  public long getEndedAt() {
    return endedAt;
  }

  public boolean isSucceeded() {
    return succeeded;
  }

  public Path getLogPath() {
    return logPath;
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    final SynchronousJobMetadata that = (SynchronousJobMetadata) o;
    return createdAt == that.createdAt && endedAt == that.endedAt && succeeded == that.succeeded && Objects.equals(id, that.id)
        && configType == that.configType && Objects.equals(configId, that.configId) && Objects.equals(logPath, that.logPath);
  }

  @Override
  public int hashCode() {
    return Objects.hash(id, configType, configId, createdAt, endedAt, succeeded, logPath);
  }

  @Override
  public String toString() {
    return "SynchronousJobMetadata{" +
        "id=" + id +
        ", configType=" + configType +
        ", configId=" + configId +
        ", createdAt=" + createdAt +
        ", endedAt=" + endedAt +
        ", succeeded=" + succeeded +
        ", logPath=" + logPath +
        '}';
  }

  public static SynchronousJobMetadata mock(final ConfigType configType) {
    final long now = Instant.now().toEpochMilli();
    final UUID configId = null;
    final boolean succeeded = true;
    final Path logPath = null;

    return new SynchronousJobMetadata(
        UUID.randomUUID(),
        configType,
        configId,
        now,
        now,
        succeeded,
        logPath);
  }

}
