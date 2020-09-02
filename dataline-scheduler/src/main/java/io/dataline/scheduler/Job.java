/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.scheduler;

import io.dataline.config.JobConfig;
import io.dataline.config.JobOutput;
import java.util.Objects;
import java.util.Optional;
import javax.annotation.Nullable;

public class Job {

  private final long id;
  private final String scope;
  private final JobStatus status;
  private final long createdAt;
  private final Long startedAt;
  private final long updatedAt;
  private final JobConfig config;
  private final JobOutput output;
  private final String stdoutPath;
  private final String stderrPath;

  public Job(long id,
             String scope,
             JobStatus status,
             JobConfig config,
             @Nullable JobOutput output,
             String stdoutPath,
             String stderrPath,
             long createdAt,
             @Nullable Long startedAt,
             long updatedAt) {
    this.id = id;
    this.scope = scope;
    this.status = status;
    this.config = config;
    this.output = output;
    this.stdoutPath = stdoutPath;
    this.stderrPath = stderrPath;
    this.createdAt = createdAt;
    this.startedAt = startedAt;
    this.updatedAt = updatedAt;
  }

  public long getId() {
    return id;
  }

  public String getScope() {
    return scope;
  }

  public JobStatus getStatus() {
    return status;
  }

  public long getCreatedAt() {
    return createdAt;
  }

  public Optional<Long> getStartedAt() {
    return Optional.ofNullable(startedAt);
  }

  public long getUpdatedAt() {
    return updatedAt;
  }

  public JobConfig getConfig() {
    return config;
  }

  public Optional<JobOutput> getOutput() {
    return Optional.ofNullable(output);
  }

  public String getStdoutPath() {
    return stdoutPath;
  }

  public String getStderrPath() {
    return stderrPath;
  }

  @Override
  public boolean equals(Object o) {
    if (this == o)
      return true;
    if (o == null || getClass() != o.getClass())
      return false;
    Job job = (Job) o;
    return id == job.id &&
        createdAt == job.createdAt &&
        updatedAt == job.updatedAt &&
        scope.equals(job.scope) &&
        status == job.status &&
        Objects.equals(startedAt, job.startedAt) &&
        config.equals(job.config) &&
        Objects.equals(output, job.output) &&
        Objects.equals(stdoutPath, job.stdoutPath) &&
        Objects.equals(stderrPath, job.stderrPath);
  }

  @Override
  public int hashCode() {
    return Objects.hash(id, scope, status, createdAt, startedAt, updatedAt, config, output, stdoutPath, stderrPath);
  }

  @Override
  public String toString() {
    return "Job{"
        + "id="
        + id
        + ", scope='"
        + scope
        + '\''
        + ", status="
        + status
        + ", createdAt="
        + createdAt
        + ", startedAt="
        + startedAt
        + ", updatedAt="
        + updatedAt
        + ", config='"
        + config
        + '\''
        + ", output="
        + output
        + ", stdoutPath='"
        + stdoutPath
        + '\''
        + ", stderrPath='"
        + stderrPath
        + '\''
        + '}';
  }

}
