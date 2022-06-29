/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.models;

import io.airbyte.config.AttemptFailureSummary;
import io.airbyte.config.JobOutput;
import java.nio.file.Path;
import java.util.Objects;
import java.util.Optional;
import javax.annotation.Nullable;

public class Attempt {

  private final long id;
  private final long jobId;
  private final JobOutput output;
  private final AttemptStatus status;
  private final AttemptFailureSummary failureSummary;
  private final Path logPath;
  private final long updatedAtInSecond;
  private final long createdAtInSecond;
  private final Long endedAtInSecond;

  public Attempt(final long id,
                 final long jobId,
                 final Path logPath,
                 final @Nullable JobOutput output,
                 final AttemptStatus status,
                 final @Nullable AttemptFailureSummary failureSummary,
                 final long createdAtInSecond,
                 final long updatedAtInSecond,
                 final @Nullable Long endedAtInSecond) {
    this.id = id;
    this.jobId = jobId;
    this.output = output;
    this.status = status;
    this.failureSummary = failureSummary;
    this.logPath = logPath;
    this.updatedAtInSecond = updatedAtInSecond;
    this.createdAtInSecond = createdAtInSecond;
    this.endedAtInSecond = endedAtInSecond;
  }

  public long getId() {
    return id;
  }

  public long getJobId() {
    return jobId;
  }

  public Optional<JobOutput> getOutput() {
    return Optional.ofNullable(output);
  }

  public AttemptStatus getStatus() {
    return status;
  }

  public Optional<AttemptFailureSummary> getFailureSummary() {
    return Optional.ofNullable(failureSummary);
  }

  public Path getLogPath() {
    return logPath;
  }

  public Optional<Long> getEndedAtInSecond() {
    return Optional.ofNullable(endedAtInSecond);
  }

  public long getCreatedAtInSecond() {
    return createdAtInSecond;
  }

  public long getUpdatedAtInSecond() {
    return updatedAtInSecond;
  }

  public static boolean isAttemptInTerminalState(final Attempt attempt) {
    return AttemptStatus.TERMINAL_STATUSES.contains(attempt.getStatus());
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    final Attempt attempt = (Attempt) o;
    return id == attempt.id &&
        jobId == attempt.jobId &&
        updatedAtInSecond == attempt.updatedAtInSecond &&
        createdAtInSecond == attempt.createdAtInSecond &&
        Objects.equals(output, attempt.output) &&
        status == attempt.status &&
        Objects.equals(failureSummary, attempt.failureSummary) &&
        Objects.equals(logPath, attempt.logPath) &&
        Objects.equals(endedAtInSecond, attempt.endedAtInSecond);
  }

  @Override
  public int hashCode() {
    return Objects.hash(id, jobId, output, status, failureSummary, logPath, updatedAtInSecond, createdAtInSecond, endedAtInSecond);
  }

  @Override
  public String toString() {
    return "Attempt{" +
        "id=" + id +
        ", jobId=" + jobId +
        ", output=" + output +
        ", status=" + status +
        ", failureSummary=" + failureSummary +
        ", logPath=" + logPath +
        ", updatedAtInSecond=" + updatedAtInSecond +
        ", createdAtInSecond=" + createdAtInSecond +
        ", endedAtInSecond=" + endedAtInSecond +
        '}';
  }

}
