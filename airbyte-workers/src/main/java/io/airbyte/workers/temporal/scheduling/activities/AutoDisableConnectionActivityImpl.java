/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static io.airbyte.metrics.lib.ApmTraceConstants.ACTIVITY_TRACE_OPERATION_NAME;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.CONNECTION_ID_KEY;
import static io.airbyte.persistence.job.JobNotifier.CONNECTION_DISABLED_NOTIFICATION;
import static io.airbyte.persistence.job.JobNotifier.CONNECTION_DISABLED_WARNING_NOTIFICATION;
import static io.airbyte.persistence.job.models.Job.REPLICATION_TYPES;
import static java.time.temporal.ChronoUnit.DAYS;

import datadog.trace.api.Trace;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.temporal.config.WorkerMode;
import io.airbyte.commons.temporal.exception.RetryableException;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.Status;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.metrics.lib.ApmTraceUtils;
import io.airbyte.persistence.job.JobNotifier;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.persistence.job.models.Job;
import io.airbyte.persistence.job.models.JobStatus;
import io.airbyte.persistence.job.models.JobWithStatusAndTimestamp;
import io.airbyte.validation.json.JsonValidationException;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.annotation.Value;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.TimeUnit;

@Singleton
@Requires(env = WorkerMode.CONTROL_PLANE)
public class AutoDisableConnectionActivityImpl implements AutoDisableConnectionActivity {

  private final ConfigRepository configRepository;
  private final JobPersistence jobPersistence;
  private final FeatureFlags featureFlags;
  private final Integer maxDaysOfOnlyFailedJobsBeforeConnectionDisable;
  private final Integer maxFailedJobsInARowBeforeConnectionDisable;
  private final JobNotifier jobNotifier;

  public AutoDisableConnectionActivityImpl(final ConfigRepository configRepository,
                                           final JobPersistence jobPersistence,
                                           final FeatureFlags featureFlags,
                                           @Value("${airbyte.worker.job.failed.max-days}") final Integer maxDaysOfOnlyFailedJobsBeforeConnectionDisable,
                                           @Value("${airbyte.worker.job.failed.max-jobs}") final Integer maxFailedJobsInARowBeforeConnectionDisable,
                                           final JobNotifier jobNotifier) {
    this.configRepository = configRepository;
    this.jobPersistence = jobPersistence;
    this.featureFlags = featureFlags;
    this.maxDaysOfOnlyFailedJobsBeforeConnectionDisable = maxDaysOfOnlyFailedJobsBeforeConnectionDisable;
    this.maxFailedJobsInARowBeforeConnectionDisable = maxFailedJobsInARowBeforeConnectionDisable;
    this.jobNotifier = jobNotifier;
  }

  // Given a connection id and current timestamp, this activity will set a connection to INACTIVE if
  // either:
  // - fails jobs consecutively and hits the `configs.getMaxFailedJobsInARowBeforeConnectionDisable()`
  // limit
  // - all the jobs in the past `configs.getMaxDaysOfOnlyFailedJobsBeforeConnectionDisable()` days are
  // failures, and that the connection's first job is at least that many days old
  // Notifications will be sent if a connection is disabled or warned if it has reached halfway to
  // disable limits
  @Trace(operationName = ACTIVITY_TRACE_OPERATION_NAME)
  @Override
  public AutoDisableConnectionOutput autoDisableFailingConnection(final AutoDisableConnectionActivityInput input) {
    ApmTraceUtils.addTagsToTrace(Map.of(CONNECTION_ID_KEY, input.getConnectionId()));
    if (featureFlags.autoDisablesFailingConnections()) {
      try {
        // if connection is already inactive, no need to disable
        final StandardSync standardSync = configRepository.getStandardSync(input.getConnectionId());
        if (standardSync.getStatus() == Status.INACTIVE) {
          return new AutoDisableConnectionOutput(false);
        }

        final int maxDaysOfOnlyFailedJobs = maxDaysOfOnlyFailedJobsBeforeConnectionDisable;
        final int maxDaysOfOnlyFailedJobsBeforeWarning = maxDaysOfOnlyFailedJobs / 2;
        final int maxFailedJobsInARowBeforeConnectionDisableWarning = maxFailedJobsInARowBeforeConnectionDisable / 2;
        final long currTimestampInSeconds = input.getCurrTimestamp().getEpochSecond();
        final Job lastJob = jobPersistence.getLastReplicationJob(input.getConnectionId())
            .orElseThrow(() -> new Exception("Auto-Disable Connection should not have been attempted if can't get latest replication job."));
        final Job firstJob = jobPersistence.getFirstReplicationJob(input.getConnectionId())
            .orElseThrow(() -> new Exception("Auto-Disable Connection should not have been attempted if no replication job has been run."));

        final List<JobWithStatusAndTimestamp> jobs = jobPersistence.listJobStatusAndTimestampWithConnection(input.getConnectionId(),
            REPLICATION_TYPES, input.getCurrTimestamp().minus(maxDaysOfOnlyFailedJobs, DAYS));

        int numFailures = 0;
        Optional<Long> successTimestamp = Optional.empty();

        for (final JobWithStatusAndTimestamp job : jobs) {
          final JobStatus jobStatus = job.getStatus();
          if (jobStatus == JobStatus.FAILED) {
            numFailures++;
          } else if (jobStatus == JobStatus.SUCCEEDED) {
            successTimestamp = Optional.of(job.getUpdatedAtInSecond());
            break;
          }
        }

        final boolean warningPreviouslySentForMaxDays =
            warningPreviouslySentForMaxDays(numFailures, successTimestamp, maxDaysOfOnlyFailedJobsBeforeWarning, firstJob, jobs);

        if (numFailures == 0) {
          return new AutoDisableConnectionOutput(false);
        } else if (numFailures >= maxFailedJobsInARowBeforeConnectionDisable) {
          // disable connection if max consecutive failed jobs limit has been hit
          disableConnection(standardSync, lastJob);
          return new AutoDisableConnectionOutput(true);
        } else if (numFailures == maxFailedJobsInARowBeforeConnectionDisableWarning && !warningPreviouslySentForMaxDays) {
          // warn if number of consecutive failures hits 50% of MaxFailedJobsInARow
          jobNotifier.autoDisableConnectionWarning(lastJob);
          // explicitly send to email if customer.io api key is set, since email notification cannot be set by
          // configs through UI yet
          jobNotifier.notifyJobByEmail(null, CONNECTION_DISABLED_WARNING_NOTIFICATION, lastJob);
          return new AutoDisableConnectionOutput(false);
        }

        // calculate the number of days this connection first tried a replication job, used to ensure not to
        // disable or warn for `maxDaysOfOnlyFailedJobs` if the first job is younger than
        // `maxDaysOfOnlyFailedJobs` days, This avoids cases such as "the very first job run was a failure".
        final int numDaysSinceFirstReplicationJob = getDaysSinceTimestamp(currTimestampInSeconds, firstJob.getCreatedAtInSecond());
        final boolean firstReplicationOlderThanMaxDisableDays = numDaysSinceFirstReplicationJob >= maxDaysOfOnlyFailedJobs;
        final boolean noPreviousSuccess = successTimestamp.isEmpty();

        // disable connection if only failed jobs in the past maxDaysOfOnlyFailedJobs days
        if (firstReplicationOlderThanMaxDisableDays && noPreviousSuccess) {
          disableConnection(standardSync, lastJob);
          return new AutoDisableConnectionOutput(true);
        }

        // skip warning if previously sent
        if (warningPreviouslySentForMaxDays || numFailures > maxFailedJobsInARowBeforeConnectionDisableWarning) {
          return new AutoDisableConnectionOutput(false);
        }

        final boolean firstReplicationOlderThanMaxDisableWarningDays = numDaysSinceFirstReplicationJob >= maxDaysOfOnlyFailedJobsBeforeWarning;
        final boolean successOlderThanPrevFailureByMaxWarningDays = // set to true if no previous success is found
            noPreviousSuccess || getDaysSinceTimestamp(currTimestampInSeconds, successTimestamp.get()) >= maxDaysOfOnlyFailedJobsBeforeWarning;

        // send warning if there are only failed jobs in the past maxDaysOfOnlyFailedJobsBeforeWarning days
        // _unless_ a warning should have already been sent in the previous failure
        if (firstReplicationOlderThanMaxDisableWarningDays && successOlderThanPrevFailureByMaxWarningDays) {
          jobNotifier.autoDisableConnectionWarning(lastJob);
          // explicitly send to email if customer.io api key is set, since email notification cannot be set by
          // configs through UI yet
          jobNotifier.notifyJobByEmail(null, CONNECTION_DISABLED_WARNING_NOTIFICATION, lastJob);
        }

      } catch (final Exception e) {
        throw new RetryableException(e);
      }
    }
    return new AutoDisableConnectionOutput(false);
  }

  // Checks to see if warning should have been sent in the previous failure, if so skip sending of
  // warning to avoid spam
  // Assume warning has been sent if either of the following is true:
  // 1. no success found in the time span and the previous failure occurred
  // maxDaysOfOnlyFailedJobsBeforeWarning days after the first job
  // 2. success found and the previous failure occurred maxDaysOfOnlyFailedJobsBeforeWarning days
  // after that success
  private boolean warningPreviouslySentForMaxDays(final int numFailures,
                                                  final Optional<Long> successTimestamp,
                                                  final int maxDaysOfOnlyFailedJobsBeforeWarning,
                                                  final Job firstJob,
                                                  final List<JobWithStatusAndTimestamp> jobs) {
    // no previous warning sent if there was no previous failure
    if (numFailures <= 1 || jobs.size() <= 1)
      return false;

    // get previous failed job (skipping first job since that's considered "current" job)
    JobWithStatusAndTimestamp prevFailedJob = jobs.get(1);
    for (int i = 2; i < jobs.size(); i++) {
      if (prevFailedJob.getStatus() == JobStatus.FAILED)
        break;
      prevFailedJob = jobs.get(i);
    }

    final boolean successExists = successTimestamp.isPresent();
    boolean successOlderThanPrevFailureByMaxWarningDays = false;
    if (successExists) {
      successOlderThanPrevFailureByMaxWarningDays =
          getDaysSinceTimestamp(prevFailedJob.getUpdatedAtInSecond(), successTimestamp.get()) >= maxDaysOfOnlyFailedJobsBeforeWarning;
    }
    final boolean prevFailureOlderThanFirstJobByMaxWarningDays =
        getDaysSinceTimestamp(prevFailedJob.getUpdatedAtInSecond(), firstJob.getUpdatedAtInSecond()) >= maxDaysOfOnlyFailedJobsBeforeWarning;

    return (successExists && successOlderThanPrevFailureByMaxWarningDays)
        || (!successExists && prevFailureOlderThanFirstJobByMaxWarningDays);
  }

  private int getDaysSinceTimestamp(final long currentTimestampInSeconds, final long timestampInSeconds) {
    return Math.toIntExact(TimeUnit.SECONDS.toDays(currentTimestampInSeconds - timestampInSeconds));
  }

  private void disableConnection(final StandardSync standardSync, final Job lastJob) throws JsonValidationException, IOException {
    standardSync.setStatus(Status.INACTIVE);
    configRepository.writeStandardSync(standardSync);

    jobNotifier.autoDisableConnection(lastJob);
    // explicitly send to email if customer.io api key is set, since email notification cannot be set by
    // configs through UI yet
    jobNotifier.notifyJobByEmail(null, CONNECTION_DISABLED_NOTIFICATION, lastJob);
  }

}
