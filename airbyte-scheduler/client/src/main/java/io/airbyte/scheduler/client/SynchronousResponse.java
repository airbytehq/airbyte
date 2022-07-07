/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.client;

import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.workers.JobStatus;
import io.airbyte.workers.temporal.TemporalResponse;
import java.util.Objects;
import java.util.UUID;

public class SynchronousResponse<T> {

  private final T output;
  private final SynchronousJobMetadata metadata;
  private JobStatus jobStatus;

  public static <T> SynchronousResponse<T> error(final SynchronousJobMetadata metadata) {
    return new SynchronousResponse<>(null, metadata, JobStatus.FAILED);
  }

  public static <T> SynchronousResponse<T> success(final T output, final SynchronousJobMetadata metadata) {
    return new SynchronousResponse<>(output, metadata, JobStatus.SUCCEEDED);
  }

  public static <T> SynchronousResponse<T> fromTemporalResponse(final TemporalResponse<T> temporalResponse,
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
        createdAt,
        endedAt);
    final JobStatus jobStatus = metadata.isSucceeded() ? JobStatus.SUCCEEDED : JobStatus.FAILED;
    return new SynchronousResponse<>(temporalResponse.getOutput().orElse(null), metadata, jobStatus);
  }

  public SynchronousResponse(final T output, final SynchronousJobMetadata metadata, final JobStatus jobStatus) {
    this.output = output;
    this.metadata = metadata;
    this.jobStatus = jobStatus;
  }

  public boolean isSuccess() {
    return jobStatus == JobStatus.SUCCEEDED;
  }

  public T getOutput() {
    return output;
  }

  public JobStatus getJobStatus() {
    return jobStatus;
  }

  public void setJobStatus(final JobStatus jobStatus) {
    this.jobStatus = jobStatus;
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
