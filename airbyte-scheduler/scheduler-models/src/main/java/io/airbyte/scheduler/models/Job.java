/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.models;

import com.google.common.base.Preconditions;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobOutput;
import java.util.Comparator;
import java.util.EnumSet;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import javax.annotation.Nullable;

public class Job {

  public static final Set<ConfigType> REPLICATION_TYPES = EnumSet.of(ConfigType.SYNC, ConfigType.RESET_CONNECTION);

  private final long id;
  private final ConfigType configType;
  private final String scope;
  private final JobConfig config;
  private final JobStatus status;
  private final Long startedAtInSecond;
  private final long createdAtInSecond;
  private final long updatedAtInSecond;
  private final List<Attempt> attempts;

  public Job(final long id,
             final ConfigType configType,
             final String scope,
             final JobConfig config,
             final List<Attempt> attempts,
             final JobStatus status,
             final @Nullable Long startedAtInSecond,
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

  public int getAttemptsCount() {
    return attempts.size();
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

  public Optional<JobOutput> getSuccessOutput() {
    return getSuccessfulAttempt().flatMap(Attempt::getOutput);
  }

  public Optional<Attempt> getLastFailedAttempt() {
    return getAttempts()
        .stream()
        .sorted(Comparator.comparing(Attempt::getCreatedAtInSecond).reversed())
        .filter(a -> a.getStatus() == AttemptStatus.FAILED)
        .findFirst();
  }

  public Optional<Attempt> getLastAttemptWithOutput() {
    return getAttempts()
        .stream()
        .sorted(Comparator.comparing(Attempt::getCreatedAtInSecond).reversed())
        .filter(a -> a.getOutput().isPresent() && a.getOutput().get().getSync() != null && a.getOutput().get().getSync().getState() != null)
        .findFirst();
  }

  public boolean hasRunningAttempt() {
    return getAttempts().stream().anyMatch(a -> !Attempt.isAttemptInTerminalState(a));
  }

  public boolean isJobInTerminalState() {
    return JobStatus.TERMINAL_STATUSES.contains(getStatus());
  }

  public void validateStatusTransition(final JobStatus newStatus) throws IllegalStateException {
    final Set<JobStatus> validNewStatuses = JobStatus.VALID_STATUS_CHANGES.get(status);

    if (!validNewStatuses.contains(newStatus)) {
      throw new IllegalStateException(String.format(
          "Transitioning Job %d from JobStatus %s to %s is not allowed. The only valid statuses that an be transitioned to from %s are %s",
          id,
          status,
          newStatus,
          status,
          JobStatus.VALID_STATUS_CHANGES.get(status)));
    }
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    final Job job = (Job) o;
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
