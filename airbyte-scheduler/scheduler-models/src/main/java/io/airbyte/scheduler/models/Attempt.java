/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.scheduler.models;

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
  private final Path logPath;
  private final long updatedAtInSecond;
  private final long createdAtInSecond;
  private final Long endedAtInSecond;

  public Attempt(final long id,
                 final long jobId,
                 final Path logPath,
                 final @Nullable JobOutput output,
                 final AttemptStatus status,
                 final long createdAtInSecond,
                 final long updatedAtInSecond,
                 final @Nullable Long endedAtInSecond) {
    this.id = id;
    this.jobId = jobId;
    this.output = output;
    this.status = status;
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

  public static boolean isAttemptInTerminalState(Attempt attempt) {
    return AttemptStatus.TERMINAL_STATUSES.contains(attempt.getStatus());
  }

  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    Attempt attempt = (Attempt) o;
    return id == attempt.id &&
        jobId == attempt.jobId &&
        updatedAtInSecond == attempt.updatedAtInSecond &&
        createdAtInSecond == attempt.createdAtInSecond &&
        Objects.equals(output, attempt.output) &&
        status == attempt.status &&
        Objects.equals(logPath, attempt.logPath) &&
        Objects.equals(endedAtInSecond, attempt.endedAtInSecond);
  }

  @Override
  public int hashCode() {
    return Objects.hash(id, jobId, output, status, logPath, updatedAtInSecond, createdAtInSecond, endedAtInSecond);
  }

  @Override
  public String toString() {
    return "Attempt{" +
        "id=" + id +
        ", jobId=" + jobId +
        ", output=" + output +
        ", status=" + status +
        ", logPath=" + logPath +
        ", updatedAtInSecond=" + updatedAtInSecond +
        ", createdAtInSecond=" + createdAtInSecond +
        ", endedAtInSecond=" + endedAtInSecond +
        '}';
  }

}
