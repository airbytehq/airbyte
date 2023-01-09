/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal;

import java.util.Objects;
import java.util.Optional;

public class TemporalResponse<T> {

  private final T output;
  private final JobMetadata metadata;

  public static <T> TemporalResponse<T> error(final JobMetadata metadata) {
    return new TemporalResponse<>(null, metadata);
  }

  public static <T> TemporalResponse<T> success(final T output, final JobMetadata metadata) {
    return new TemporalResponse<>(output, metadata);
  }

  public TemporalResponse(final T output, final JobMetadata metadata) {
    this.output = output;
    this.metadata = metadata;
  }

  public boolean isSuccess() {
    return metadata.isSucceeded();
  }

  /**
   * Returns the output of the Temporal job.
   *
   * @return The output of the Temporal job. Empty if no output or if the job failed.
   */
  public Optional<T> getOutput() {
    return Optional.ofNullable(output);
  }

  public JobMetadata getMetadata() {
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
    final TemporalResponse<?> that = (TemporalResponse<?>) o;
    return Objects.equals(output, that.output) && Objects.equals(metadata, that.metadata);
  }

  @Override
  public int hashCode() {
    return Objects.hash(output, metadata);
  }

  @Override
  public String toString() {
    return "TemporalResponse{" +
        "output=" + output +
        ", metadata=" + metadata +
        '}';
  }

}
