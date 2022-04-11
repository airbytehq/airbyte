/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static io.airbyte.scheduler.models.Job.REPLICATION_TYPES;

import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.config.Configs;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.Status;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.workers.temporal.exception.RetryableException;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import lombok.AllArgsConstructor;

@AllArgsConstructor
public class AutoDisableConnectionActivityImpl implements AutoDisableConnectionActivity {

  private ConfigRepository configRepository;
  private JobPersistence jobPersistence;
  private FeatureFlags featureFlags;
  private Configs configs;

  // Given a connection id and current timestamp, this activity will set a connection to INACTIVE if
  // either:
  // - fails jobs consecutively and hits the `configs.getMaxFailedJobsInARowBeforeConnectionDisable()`
  // limit
  // - all the jobs in the past `configs.getMaxDaysOfOnlyFailedJobsBeforeConnectionDisable()` days are
  // failures, and that the connection's first job is at least that many days old
  @Override
  public AutoDisableConnectionOutput autoDisableFailingConnection(final AutoDisableConnectionActivityInput input) {
    if (featureFlags.autoDisablesFailingConnections()) {
      try {
        final int maxDaysOfOnlyFailedJobs = configs.getMaxDaysOfOnlyFailedJobsBeforeConnectionDisable();
        final List<JobStatus> jobStatuses = jobPersistence.listJobStatusWithConnection(input.getConnectionId(), REPLICATION_TYPES,
            input.getCurrTimestamp().minus(maxDaysOfOnlyFailedJobs, ChronoUnit.DAYS));

        int numFailures = 0;

        // jobs are sorted from most recent to least recent
        for (final JobStatus jobStatus : jobStatuses) {
          if (jobStatus == JobStatus.FAILED) {
            numFailures++;
            if (numFailures == configs.getMaxFailedJobsInARowBeforeConnectionDisable())
              break;
          } else if (jobStatus == JobStatus.SUCCEEDED) {
            return new AutoDisableConnectionOutput(false);
          }
        }

        // if the jobs in the last 14 days don't include any succeeded or failed jobs (e.g. only cancelled
        // jobs), do not auto-disable
        if (numFailures == 0) {
          return new AutoDisableConnectionOutput(false);
        }

        // if the very first job of a connection fails, it will hit the condition of "only failed jobs in
        // the past `maxDaysOfOnlyFailedJobs` days", to avoid this behavior, we ensure that this condition
        // is only taken into account if the connection has a job that's at least `maxDaysOfOnlyFailedJobs`
        // days old
        if (numFailures != configs.getMaxFailedJobsInARowBeforeConnectionDisable()) {
          final Optional<Job> optionalFirstJob = jobPersistence.getFirstReplicationJob(input.getConnectionId());
          if (optionalFirstJob.isPresent()) {
            final long timeBetweenCurrTimestampAndFirstJob = input.getCurrTimestamp().getEpochSecond()
                - optionalFirstJob.get().getCreatedAtInSecond();
            if (timeBetweenCurrTimestampAndFirstJob <= TimeUnit.DAYS.toSeconds(maxDaysOfOnlyFailedJobs)) {
              return new AutoDisableConnectionOutput(false);
            }
          }
        }

        final StandardSync standardSync = configRepository.getStandardSync(input.getConnectionId());
        standardSync.setStatus(Status.INACTIVE);
        configRepository.writeStandardSync(standardSync);
      } catch (final Exception e) {
        throw new RetryableException(e);
      }
    }
    return new AutoDisableConnectionOutput(true);
  }

}
