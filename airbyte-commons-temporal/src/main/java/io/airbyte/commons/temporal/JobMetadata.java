/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal;

import java.nio.file.Path;
import java.util.Objects;

public class JobMetadata {

  private final boolean succeeded;
  private final Path logPath;

  public JobMetadata(final boolean succeeded, final Path logPath) {
    this.succeeded = succeeded;
    this.logPath = logPath;
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
    final JobMetadata that = (JobMetadata) o;
    return succeeded == that.succeeded && Objects.equals(logPath, that.logPath);
  }

  @Override
  public int hashCode() {
    return Objects.hash(succeeded, logPath);
  }

  @Override
  public String toString() {
    return "JobMetadata{" +
        "succeeded=" + succeeded +
        ", logPath=" + logPath +
        '}';
  }

}
