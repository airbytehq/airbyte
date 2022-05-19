/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.config.Configs;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.Status;
import io.airbyte.config.helpers.ScheduleHelpers;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.temporal.exception.RetryableException;
import java.io.IOException;
import java.time.Duration;
import java.util.Optional;
import java.util.function.Supplier;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@AllArgsConstructor
@Slf4j
public class ConfigFetchActivityImpl implements ConfigFetchActivity {

  private ConfigRepository configRepository;
  private JobPersistence jobPersistence;
  private Configs configs;
  private Supplier<Long> currentSecondsSupplier;

  @Override
  public ScheduleRetrieverOutput getTimeToWait(final ScheduleRetrieverInput input) {
    final boolean noSchedule;

    try {
      final StandardSync standardSync = configRepository.getStandardSync(input.getConnectionId());
      // Schedule and Schedule may overlap while transitioning the code to ScheduleType
      noSchedule = standardSync.getSchedule() == null && standardSync.getScheduleType() == null;
      if (noSchedule || (standardSync.getStatus() == Status.INACTIVE)) {
        // Manual syncs wait for their first run
        return new ScheduleRetrieverOutput(Duration.ofDays(100 * 365));
      }

      final Optional<Job> previousJobOptional = jobPersistence.getLastReplicationJob(input.getConnectionId());

      if (previousJobOptional.isEmpty() && noSchedule) {
        // Non-manual syncs don't wait for their first run
        return new ScheduleRetrieverOutput(Duration.ZERO);
      }

      final Job previousJob = previousJobOptional.get();
      final long prevRunStart = previousJob.getStartedAtInSecond().orElse(previousJob.getCreatedAtInSecond());
      long time_interval_schedule = 0;
      if (standardSync.getSchedule() != null) {
        time_interval_schedule = ScheduleHelpers.getIntervalInSecond(standardSync.getSchedule());
      } else if (standardSync.getScheduleType() != null){
        // i don't understand how to detect the enum type here
        time_interval_schedule = ScheduleHelpers.getIntervalInSecond(standardSync.getScheduleType());
      }

      final long nextRunStart = prevRunStart + time_interval_schedule;

      final Duration timeToWait = Duration.ofSeconds(
          Math.max(0, nextRunStart - currentSecondsSupplier.get()));

      return new ScheduleRetrieverOutput(timeToWait);
    } catch (final IOException | JsonValidationException | ConfigNotFoundException e) {
      throw new RetryableException(e);
    }
  }

  @Override
  public GetMaxAttemptOutput getMaxAttempt() {
    return new GetMaxAttemptOutput(configs.getSyncJobMaxAttempts());
  }

}
