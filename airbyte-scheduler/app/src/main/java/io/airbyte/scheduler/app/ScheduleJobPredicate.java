/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.app;

import io.airbyte.config.StandardSync;
import io.airbyte.scheduler.ScheduleHelper;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import java.time.Instant;
import java.util.Optional;
import java.util.function.BiPredicate;
import java.util.function.Supplier;

public class ScheduleJobPredicate implements BiPredicate<Optional<Job>, StandardSync> {

  private final Supplier<Instant> timeSupplier;

  public ScheduleJobPredicate(final Supplier<Instant> timeSupplier) {
    this.timeSupplier = timeSupplier;
  }

  @Override
  public boolean test(final Optional<Job> previousJobOptional, final StandardSync standardSync) {
    // if manual scheduler, then we never programmatically schedule.
    if (standardSync.getManual()) {
      return false;
    }

    final boolean timeForNewJob = isTimeForNewJob(previousJobOptional, standardSync);
    return shouldSchedule(previousJobOptional, timeForNewJob);
  }

  @SuppressWarnings("OptionalUsedAsFieldOrParameterType")
  private boolean shouldSchedule(final Optional<Job> previousJobOptional, final boolean timeForJobNewJob) {
    if (previousJobOptional.isEmpty()) {
      return true;
    }

    final Job previousJob = previousJobOptional.get();
    return switch (previousJob.getStatus()) {
      case CANCELLED, SUCCEEDED, FAILED -> timeForJobNewJob;
      case INCOMPLETE, PENDING, RUNNING -> false;
      default -> throw new IllegalArgumentException("Unrecognized status: " + previousJob.getStatus());
    };
  }

  @SuppressWarnings("OptionalUsedAsFieldOrParameterType")
  private boolean isTimeForNewJob(final Optional<Job> previousJobOptional, final StandardSync standardSync) {
    // if non-manual scheduler, and there has never been a previous run, always schedule.
    if (previousJobOptional.isEmpty()) {
      return true;
    }

    final Job previousJob = previousJobOptional.get();

    // if there is an active job, do not start a new one.
    if (!JobStatus.TERMINAL_STATUSES.contains(previousJob.getStatus())) {
      return false;
    }

    var prevRunStart = previousJob.getStartedAtInSecond().orElse(previousJob.getCreatedAtInSecond());
    var interval = ScheduleHelper.intervalInSeconds(standardSync.getSchedule());
    long nextRunStart = prevRunStart + interval;
    return nextRunStart < timeSupplier.get().getEpochSecond();
  }

}
