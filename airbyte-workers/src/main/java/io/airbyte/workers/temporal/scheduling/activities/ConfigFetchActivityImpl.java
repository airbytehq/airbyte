/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.config.StandardSync;
import io.airbyte.config.helpers.ScheduleHelpers;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.temporal.exception.NonRetryableException;
import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import java.util.Optional;
import lombok.AllArgsConstructor;

@AllArgsConstructor
public class ConfigFetchActivityImpl implements ConfigFetchActivity {

  private ConfigRepository configPersistence;
  private JobPersistence jobPersistence;

  @Override
  public ScheduleRetrieverOutput getPeriodicity(final ScheduleRetrieverInput input) {
    try {
      final Optional<Job> previousJobOptional = jobPersistence.getLastReplicationJob(input.getConnectionId());

      // if non-manual scheduler, and there has never been a previous run, always schedule.
      if (previousJobOptional.isEmpty()) {
        return new ScheduleRetrieverOutput(Duration.ZERO);
      }

      final Job previousJob = previousJobOptional.get();

      final long prevRunStart = previousJob.getStartedAtInSecond().orElse(previousJob.getCreatedAtInSecond());
      final StandardSync standardSync = configPersistence.getStandardSync(input.getConnectionId());
      final long nextRunStart = prevRunStart + ScheduleHelpers.getIntervalInSecond(standardSync.getSchedule());

      final Duration timeToWait = Duration.ofSeconds(
          Math.max(0, nextRunStart - Instant.now().getEpochSecond()));

      return new ScheduleRetrieverOutput(timeToWait);
    } catch (final IOException | JsonValidationException | ConfigNotFoundException e) {
      throw new NonRetryableException(e);
    }
  }

}
