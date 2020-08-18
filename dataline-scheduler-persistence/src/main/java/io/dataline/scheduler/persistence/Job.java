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

package io.dataline.scheduler.persistence;

import io.dataline.config.JobConfig;
import io.dataline.config.JobOutput;
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
  private final String stdout_path;
  private final String stderr_path;

  public Job(
      long id,
      String scope,
      JobStatus status,
      JobConfig config,
      @Nullable JobOutput output,
      String stdout_path,
      String stderr_path,
      long createdAt,
      @Nullable Long startedAt,
      long updatedAt) {
    this.id = id;
    this.scope = scope;
    this.status = status;
    this.config = config;
    this.output = output;
    this.stdout_path = stdout_path;
    this.stderr_path = stderr_path;
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

  public String getStdout_path() {
    return stdout_path;
  }

  public String getStderr_path() {
    return stderr_path;
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
        + ", stdout_path='"
        + stdout_path
        + '\''
        + ", stderr_path='"
        + stderr_path
        + '\''
        + '}';
  }
}
