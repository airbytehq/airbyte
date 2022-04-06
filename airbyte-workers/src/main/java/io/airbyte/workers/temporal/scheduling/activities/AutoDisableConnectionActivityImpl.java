/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static io.airbyte.scheduler.models.Job.REPLICATION_TYPES;
import static io.airbyte.scheduler.persistence.JobNotifier.CONNECTION_DISABLED_NOTIFICATION;
import static io.airbyte.scheduler.persistence.JobNotifier.CONNECTION_DISABLED_WARNING_NOTIFICATION;

import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.config.Configs;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.Status;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import io.airbyte.scheduler.persistence.JobNotifier;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.temporal.exception.RetryableException;
import java.io.IOException;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import lombok.AllArgsConstructor;

@AllArgsConstructor
public class AutoDisableConnectionActivityImpl implements AutoDisableConnectionActivity {

  private ConfigRepository configRepository;
  private JobPersistence jobPersistence;
  private FeatureFlags featureFlags;
  private Configs configs;
  private JobNotifier jobNotifier;

  // Given a connection id and current timestamp, this activity will set a connection to INACTIVE if
  // either:
  // - fails jobs consecutively and hits the `configs.getMaxFailedJobsInARowBeforeConnectionDisable()`
  // limit
  // - all the jobs in the past `configs.getMaxDaysOfOnlyFailedJobsBeforeConnectionDisable()` days are
  // failures, and that the connection's first job is at least that many days old
  // Notifications will be sent if a connection is disabled or warned if it has reached halfway to
  // disable limits
  @Override
  public AutoDisableConnectionOutput autoDisableFailingConnection(final AutoDisableConnectionActivityInput input) {
    if (featureFlags.autoDisablesFailingConnections()) {
      try {
        final int maxDaysOfOnlyFailedJobs = configs.getMaxDaysOfOnlyFailedJobsBeforeConnectionDisable();
        final int maxDaysOfOnlyFailedJobsBeforeWarning = maxDaysOfOnlyFailedJobs / 2;
        final int maxFailedJobsInARowBeforeConnectionDisableWarning = configs.getMaxFailedJobsInARowBeforeConnectionDisable() / 2;

        final List<JobStatus> jobStatuses = jobPersistence.listJobStatusWithConnection(input.getConnectionId(), REPLICATION_TYPES,
            input.getCurrTimestamp().minus(maxDaysOfOnlyFailedJobs, ChronoUnit.DAYS));

        // list of job statuses to be used in deciding if a warning should be sent; subset of `jobStatuses`
        final List<JobStatus> jobStatusesForWarning = jobPersistence.listJobStatusWithConnection(input.getConnectionId(), REPLICATION_TYPES,
            input.getCurrTimestamp().minus(maxDaysOfOnlyFailedJobsBeforeWarning, ChronoUnit.DAYS));

        final Job lastJob;
        final Optional<Job> optionalJob = jobPersistence.getLastReplicationJob(input.getConnectionId());
        if (optionalJob.isPresent()) {
          lastJob = optionalJob.get();
        } else {
          throw new Exception("Auto-Disable Connection should not have been attempted if can't get latest replication job.");
        }

        boolean hitDaysFailingWarningLimit = false;
        boolean successFound = false;
        int numFailures = 0;

        // jobs are sorted from most recent to least recent
        for (int i = 0; i < jobStatuses.size(); i++) {
          final JobStatus jobStatus = jobStatuses.get(i);
          if (jobStatus == JobStatus.FAILED) {
            numFailures++;
            if (numFailures == configs.getMaxFailedJobsInARowBeforeConnectionDisable()) {
              disableConnection(input.getConnectionId(), lastJob);
              return new AutoDisableConnectionOutput(true);
            }
          } else if (jobStatus == JobStatus.SUCCEEDED) {
            successFound = true;
            break;
          }

          // enters this if statement if only failures found in the past maxDaysOfOnlyFailedJobsBeforeWarning
          // days
          if (i == jobStatusesForWarning.size() - 1 && numFailures > 0) {
            hitDaysFailingWarningLimit = true;
          }
        }

        // if the jobs in the last maxDaysOfOnlyFailedJobs days don't include any succeeded or failed jobs
        // (e.g. only cancelled jobs), do not auto-disable and do not send any warnings
        if (numFailures == 0) {
          return new AutoDisableConnectionOutput(false);
        }

        // calculate the number of days this connection first tried a replication job, used to ensure not to
        // disable or warn for `maxDaysOfOnlyFailedJobs` if the first job is younger than
        // `maxDaysOfOnlyFailedJobs` days, This avoids cases such as "the very first job run was a failure"
        int numDaysSinceFirstReplicationJob = 0;
        final Optional<Job> optionalFirstJob =
            jobPersistence.getFirstReplicationJob(input.getConnectionId());
        if (optionalFirstJob.isPresent()) {
          final long timeBetweenCurrTimestampAndFirstJob =
              input.getCurrTimestamp().getEpochSecond() - optionalFirstJob.get().getCreatedAtInSecond();
          numDaysSinceFirstReplicationJob = Math.toIntExact(TimeUnit.SECONDS.toDays(timeBetweenCurrTimestampAndFirstJob));
        }

        if (numDaysSinceFirstReplicationJob >= maxDaysOfOnlyFailedJobs && !successFound) {
          disableConnection(input.getConnectionId(), lastJob);
          return new AutoDisableConnectionOutput(true);
        } else if (numFailures == maxFailedJobsInARowBeforeConnectionDisableWarning
            || (hitDaysFailingWarningLimit && numDaysSinceFirstReplicationJob >= maxDaysOfOnlyFailedJobsBeforeWarning)) {
          jobNotifier.autoDisableConnectionAlertWithoutCustomerioConfig(CONNECTION_DISABLED_WARNING_NOTIFICATION, lastJob);
          return new AutoDisableConnectionOutput(false);
        }

      } catch (final Exception e) {
        throw new RetryableException(e);
      }
    }
    return new AutoDisableConnectionOutput(false);
  }

  private void disableConnection(final UUID connectionId, final Job lastJob) throws JsonValidationException, IOException, ConfigNotFoundException {
    final StandardSync standardSync = configRepository.getStandardSync(connectionId);
    standardSync.setStatus(Status.INACTIVE);
    configRepository.writeStandardSync(standardSync);

    jobNotifier.autoDisableConnectionAlertWithoutCustomerioConfig(CONNECTION_DISABLED_NOTIFICATION, lastJob);
  }

}
