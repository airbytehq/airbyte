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

package io.airbyte.scheduler;

import io.airbyte.config.JobConfig;
import io.airbyte.config.JobOutput;
import java.util.Objects;
import java.util.Optional;
import javax.annotation.Nullable;

public class Job {

  private final long id;
  private final String scope;
  private final JobConfig config;
  private final String logPath;
  private final JobOutput output;
  private final int attempts;
  private final JobStatus status;
  private final Long startedAtInSecond;
  private final long createdAtInSecond;
  private final long updatedAtInSecond;

  public Job(final long id,
             final String scope,
             final JobConfig config,
             final String logPath,
             final @Nullable JobOutput output,
             final int attempts,
             final JobStatus status,
             final @Nullable Long startedAtInSecond,
             final long createdAtInSecond,
             final long updatedAtInSecond) {
    this.id = id;
    this.scope = scope;
    this.config = config;
    this.logPath = logPath;
    this.output = output;
    this.attempts = attempts;
    this.status = status;
    this.startedAtInSecond = startedAtInSecond;
    this.createdAtInSecond = createdAtInSecond;
    this.updatedAtInSecond = updatedAtInSecond;
  }

  public long getId() {
    return id;
  }

  public String getScope() {
    return scope;
  }

  public JobConfig getConfig() {
    return config;
  }

  public String getLogPath() {
    return logPath;
  }

  public Optional<JobOutput> getOutput() {
    return Optional.ofNullable(output);
  }

  public int getAttempts() {
    return attempts;
  }

  public JobStatus getStatus() {
    return status;
  }

  public Optional<Long> getStartedAtInSecond() {
    return Optional.ofNullable(startedAtInSecond);
  }

  public long getCreatedAtInSecond() {
    return createdAtInSecond;
  }

  public long getUpdatedAtInSecond() {
    return updatedAtInSecond;
  }

  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    Job job = (Job) o;
    return id == job.id &&
        Objects.equals(scope, job.scope) &&
        Objects.equals(config, job.config) &&
        Objects.equals(logPath, job.logPath) &&
        Objects.equals(output, job.output) &&
        attempts == job.attempts &&
        status == job.status &&
        Objects.equals(startedAtInSecond, job.startedAtInSecond) &&
        createdAtInSecond == job.createdAtInSecond &&
        updatedAtInSecond == job.updatedAtInSecond;
  }

  @Override
  public int hashCode() {
    return Objects.hash(id, scope, config, logPath, output, attempts, status, startedAtInSecond, createdAtInSecond, updatedAtInSecond);
  }

  @Override
  public String toString() {
    return "Job{" +
        "id=" + id +
        ", scope='" + scope + '\'' +
        ", config=" + config +
        ", logPath='" + logPath + '\'' +
        ", output=" + output +
        ", attempts=" + attempts +
        ", status=" + status +
        ", startedAtInSecond=" + startedAtInSecond +
        ", createdAtInSecond=" + createdAtInSecond +
        ", updatedAtInSecond=" + updatedAtInSecond +
        '}';
  }

}
