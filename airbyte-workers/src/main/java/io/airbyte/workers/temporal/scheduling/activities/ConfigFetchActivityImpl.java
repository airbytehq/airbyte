/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.config.Configs;
import io.airbyte.config.Cron;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.ScheduleType;
import io.airbyte.config.StandardSync.Status;
import io.airbyte.config.helpers.ScheduleHelpers;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.temporal.exception.RetryableException;
import java.io.IOException;
import java.text.ParseException;
import java.time.DateTimeException;
import java.time.Duration;
import java.util.Date;
import java.util.Optional;
import java.util.TimeZone;
import java.util.UUID;
import java.util.function.Supplier;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.joda.time.DateTimeZone;
import org.quartz.CronExpression;

@AllArgsConstructor
@Slf4j
public class ConfigFetchActivityImpl implements ConfigFetchActivity {

  private ConfigRepository configRepository;
  private JobPersistence jobPersistence;
  private Configs configs;
  private Supplier<Long> currentSecondsSupplier;

  @Override
  public ScheduleRetrieverOutput getTimeToWait(final ScheduleRetrieverInput input) {
    try {
      final StandardSync standardSync = configRepository.getStandardSync(input.getConnectionId());

      if (standardSync.getScheduleType() != null) {
        return this.getTimeToWaitFromScheduleType(standardSync, input.getConnectionId());
      }
      return this.getTimeToWaitFromLegacy(standardSync, input.getConnectionId());
    } catch (final IOException | JsonValidationException | ConfigNotFoundException e) {
      throw new RetryableException(e);
    }
  }

  private ScheduleRetrieverOutput getTimeToWaitFromScheduleType(final StandardSync standardSync, UUID connectionId) throws IOException {
    if (standardSync.getScheduleType() == ScheduleType.MANUAL || standardSync.getStatus() != Status.ACTIVE) {
      // Manual syncs wait for their first run
      return new ScheduleRetrieverOutput(Duration.ofDays(100 * 365));
    }

    final Optional<Job> previousJobOptional = jobPersistence.getLastReplicationJob(connectionId);

    if (standardSync.getScheduleType() == ScheduleType.BASIC_SCHEDULE) {
      if (previousJobOptional.isEmpty()) {
        // Basic schedules don't wait for their first run.
        return new ScheduleRetrieverOutput(Duration.ZERO);
      }
      final Job previousJob = previousJobOptional.get();
      final long prevRunStart = previousJob.getStartedAtInSecond().orElse(previousJob.getCreatedAtInSecond());
      final long nextRunStart = prevRunStart + ScheduleHelpers.getIntervalInSecond(standardSync.getSchedule().getBasicSchedule());
      final Duration timeToWait = Duration.ofSeconds(
          Math.max(0, nextRunStart - currentSecondsSupplier.get()));
      return new ScheduleRetrieverOutput(timeToWait);
    }

    else { // standardSync.getScheduleType() == ScheduleType.CRON
      final Cron scheduleCron = standardSync.getSchedule().getCron();
      final TimeZone timeZone = DateTimeZone.forID(scheduleCron.getCronTimeZone()).toTimeZone();
      try {
        final CronExpression cronExpression = new CronExpression(scheduleCron.getCronExpression());
        cronExpression.setTimeZone(timeZone);
        final Date nextRunStart = cronExpression.getNextValidTimeAfter(new Date(currentSecondsSupplier.get() * 1000L));
        final Duration timeToWait = Duration.ofSeconds(
            Math.max(0, nextRunStart.getTime() / 1000L - currentSecondsSupplier.get()));
        return new ScheduleRetrieverOutput(timeToWait);
      } catch (ParseException e) {
        throw new DateTimeException(e.getMessage());
      }
    }
  }

  private ScheduleRetrieverOutput getTimeToWaitFromLegacy(final StandardSync standardSync, UUID connectionId) throws IOException {
    if (standardSync.getSchedule() == null || standardSync.getStatus() != Status.ACTIVE) {
      // Manual syncs wait for their first run
      return new ScheduleRetrieverOutput(Duration.ofDays(100 * 365));
    }

    final Optional<Job> previousJobOptional = jobPersistence.getLastReplicationJob(connectionId);

    if (previousJobOptional.isEmpty() && standardSync.getSchedule() != null) {
      // Non-manual syncs don't wait for their first run
      return new ScheduleRetrieverOutput(Duration.ZERO);
    }

    final Job previousJob = previousJobOptional.get();
    final long prevRunStart = previousJob.getStartedAtInSecond().orElse(previousJob.getCreatedAtInSecond());

    final long nextRunStart = prevRunStart + ScheduleHelpers.getIntervalInSecond(standardSync.getSchedule());

    final Duration timeToWait = Duration.ofSeconds(
        Math.max(0, nextRunStart - currentSecondsSupplier.get()));

    return new ScheduleRetrieverOutput(timeToWait);

  }

  @Override
  public GetMaxAttemptOutput getMaxAttempt() {
    return new GetMaxAttemptOutput(configs.getSyncJobMaxAttempts());
  }

}
