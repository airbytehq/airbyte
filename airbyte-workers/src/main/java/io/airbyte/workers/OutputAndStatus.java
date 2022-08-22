/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import java.util.Objects;
import java.util.Optional;
import org.apache.commons.lang3.builder.ToStringBuilder;

public class OutputAndStatus<OutputType> {

  private final OutputType output;
  private final JobStatus status;

  public OutputAndStatus(final JobStatus status, final OutputType output) {
    this.output = output;
    this.status = status;
  }

  public OutputAndStatus(final JobStatus status) {
    this.status = status;
    this.output = null;
  }

  @Override
  public String toString() {
    return new ToStringBuilder(this).append(status).append(output).build();
  }

  public Optional<OutputType> getOutput() {
    return Optional.ofNullable(output);
  }

  public JobStatus getStatus() {
    return status;
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    final OutputAndStatus<?> that = (OutputAndStatus<?>) o;
    return Objects.equals(output, that.output) &&
        status == that.status;
  }

  @Override
  public int hashCode() {
    return Objects.hash(output, status);
  }

}
