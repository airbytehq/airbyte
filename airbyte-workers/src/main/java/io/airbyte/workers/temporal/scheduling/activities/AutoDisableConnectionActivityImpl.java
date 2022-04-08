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

        final Optional<Job> optionalJob = jobPersistence.getLastReplicationJob(input.getConnectionId());
        final Job lastJob = optionalJob
            .orElseThrow(() -> new Exception("Auto-Disable Connection should not have been attempted if can't get latest replication job."));

        final int numFailuresForDisable = getNumOfFailuresBeforeSuccess(input, maxDaysOfOnlyFailedJobs);
        // if the jobs in the last maxDaysOfOnlyFailedJobs days don't include any succeeded or failed jobs
        // (e.g. only cancelled jobs), do not auto-disable and do not send any warnings
        if (numFailuresForDisable == 0) {
          return new AutoDisableConnectionOutput(false);
        } else if (Math.abs(numFailuresForDisable) == configs.getMaxFailedJobsInARowBeforeConnectionDisable()) {
          disableConnection(input.getConnectionId(), lastJob);
          return new AutoDisableConnectionOutput(true);
        }

        // calculate the number of days this connection first tried a replication job, used to ensure not to
        // disable or warn for `maxDaysOfOnlyFailedJobs` if the first job is younger than
        // `maxDaysOfOnlyFailedJobs` days, This avoids cases such as "the very first job run was a failure"
        final int numDaysSinceFirstReplicationJob = getNumDaysSinceFirstReplicationJob(input);
        final boolean successFound = numFailuresForDisable < 0;

        if (numDaysSinceFirstReplicationJob >= maxDaysOfOnlyFailedJobs && !successFound) {
          disableConnection(input.getConnectionId(), lastJob);
          return new AutoDisableConnectionOutput(true);
        }

        // warn if number of failures hits maxFailedJobsInARowBeforeConnectionDisableWarning
        if (Math.abs(numFailuresForDisable) == maxFailedJobsInARowBeforeConnectionDisableWarning) {
          jobNotifier.autoDisableConnectionAlertWithoutCustomerioConfig(CONNECTION_DISABLED_WARNING_NOTIFICATION, lastJob);
        }

        // warn if only failures in the past maxDaysOfOnlyFailedJobsBeforeWarning days
        final int numFailuresForWarning = getNumOfFailuresBeforeSuccess(input, maxDaysOfOnlyFailedJobsBeforeWarning);
        if ((numFailuresForWarning > 0 && numDaysSinceFirstReplicationJob >= maxDaysOfOnlyFailedJobsBeforeWarning)) {
          jobNotifier.autoDisableConnectionAlertWithoutCustomerioConfig(CONNECTION_DISABLED_WARNING_NOTIFICATION, lastJob);
        }

      } catch (final Exception e) {
        throw new RetryableException(e);
      }
    }
    return new AutoDisableConnectionOutput(false);
  }

  // The absolute value of the return int will be the number of consecutive failures before a success
  // if found. The input list of JobStatuses is expected to be ordered from most recent to least
  // recent. If a success is found, the return value will be a negative int, while if there are no
  // successes found, the return value will be a positive int.
  private int getNumOfFailuresBeforeSuccess(final AutoDisableConnectionActivityInput input, final int lookBackInDays) throws IOException {
    final List<JobStatus> jobStatuses = jobPersistence.listJobStatusWithConnection(input.getConnectionId(), REPLICATION_TYPES,
        input.getCurrTimestamp().minus(lookBackInDays, ChronoUnit.DAYS));

    int numFailures = 0;
    for (final JobStatus jobStatus : jobStatuses) {
      if (jobStatus == JobStatus.FAILED) {
        numFailures++;
      } else if (jobStatus == JobStatus.SUCCEEDED) {
        numFailures = numFailures * -1;
        break;
      }
    }

    return numFailures;
  }

  private int getNumDaysSinceFirstReplicationJob(final AutoDisableConnectionActivityInput input) throws Exception {
    final Optional<Job> optionalFirstJob = jobPersistence.getFirstReplicationJob(input.getConnectionId());
    final Job firstJob = optionalFirstJob
        .orElseThrow(() -> new Exception("Auto-Disable Connection should not have been attempted if no replication job has been run."));

    final long timeBetweenCurrTimestampAndFirstJob =
        input.getCurrTimestamp().getEpochSecond() - firstJob.getCreatedAtInSecond();
    return Math.toIntExact(TimeUnit.SECONDS.toDays(timeBetweenCurrTimestampAndFirstJob));
  }

  private void disableConnection(final UUID connectionId, final Job lastJob) throws JsonValidationException, IOException, ConfigNotFoundException {
    final StandardSync standardSync = configRepository.getStandardSync(connectionId);
    standardSync.setStatus(Status.INACTIVE);
    configRepository.writeStandardSync(standardSync);

    jobNotifier.autoDisableConnectionAlertWithoutCustomerioConfig(CONNECTION_DISABLED_NOTIFICATION, lastJob);
  }

}
