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

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.google.common.base.Preconditions;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobOutput;
import java.util.EnumSet;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import javax.annotation.Nullable;

public class Job {

  public static final Set<ConfigType> REPLICATION_TYPES = EnumSet.of(ConfigType.SYNC, ConfigType.RESET_CONNECTION);

  public long id;

  public ConfigType configType;

  public String scope;

  public JobConfig config;

  public JobStatus status;

  public long startedAtInSecond;

  public long createdAtInSecond;

  public long updatedAtInSecond;

  public List<Attempt> attempts;

  public Job() {

  }

  public Job(final long id,
             final ConfigType configType,
             final String scope,
             final JobConfig config,
             final List<Attempt> attempts,
             final JobStatus status,
             final long startedAtInSecond,
             final long createdAtInSecond,
             final long updatedAtInSecond) {
    this.id = id;
    this.configType = configType;
    this.scope = scope;
    this.config = config;
    this.attempts = attempts;
    this.status = status;
    this.startedAtInSecond = startedAtInSecond;
    this.createdAtInSecond = createdAtInSecond;
    this.updatedAtInSecond = updatedAtInSecond;
  }

  public long getId() {
    return id;
  }

  public ConfigType getConfigType() {
    return configType;
  }

  public String getScope() {
    return scope;
  }

  public JobConfig getConfig() {
    return config;
  }

  public List<Attempt> getAttempts() {
    return attempts;
  }

  @JsonIgnore
  public int getAttemptsCount() {
    return attempts.size();
  }

  public JobStatus getStatus() {
    return status;
  }

  public long getStartedAtInSecond() {
    return startedAtInSecond;
  }

  public long getCreatedAtInSecond() {
    return createdAtInSecond;
  }

  public long getUpdatedAtInSecond() {
    return updatedAtInSecond;
  }

  @JsonIgnore
  public Optional<Attempt> getSuccessfulAttempt() {
    final List<Attempt> successfulAttempts = getAttempts()
        .stream()
        .filter(a -> a.getStatus() == AttemptStatus.SUCCEEDED)
        .collect(Collectors.toList());

    Preconditions.checkState(successfulAttempts.size() <= 1, String.format("Job %s has multiple successful attempts.", getId()));
    if (successfulAttempts.size() == 1) {
      return Optional.of(successfulAttempts.get(0));
    } else {
      return Optional.empty();
    }
  }

  @JsonIgnore
  public Optional<JobOutput> getSuccessOutput() {
    return getSuccessfulAttempt().flatMap(x -> Optional.ofNullable(x.getOutput()));
  }

  @JsonIgnore
  public boolean hasRunningAttempt() {
    return getAttempts().stream().anyMatch(a -> !Attempt.isAttemptInTerminalState(a));
  }

  @JsonIgnore
  public boolean isJobInTerminalState() {
    return JobStatus.TERMINAL_STATUSES.contains(getStatus());
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
        createdAtInSecond == job.createdAtInSecond &&
        updatedAtInSecond == job.updatedAtInSecond &&
        Objects.equals(scope, job.scope) &&
        Objects.equals(config, job.config) &&
        status == job.status &&
        Objects.equals(startedAtInSecond, job.startedAtInSecond) &&
        Objects.equals(attempts, job.attempts);
  }

  @Override
  public int hashCode() {
    return Objects.hash(id, scope, config, status, startedAtInSecond, createdAtInSecond, updatedAtInSecond, attempts);
  }

  @Override
  public String toString() {
    return "Job{" +
        "id=" + id +
        ", scope='" + scope + '\'' +
        ", config=" + config +
        ", status=" + status +
        ", startedAtInSecond=" + startedAtInSecond +
        ", createdAtInSecond=" + createdAtInSecond +
        ", updatedAtInSecond=" + updatedAtInSecond +
        ", attempts=" + attempts +
        '}';
  }

}
