/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.config.BasicSchedule;
import io.airbyte.config.Configs;
import io.airbyte.config.Cron;
import io.airbyte.config.Schedule;
import io.airbyte.config.ScheduleData;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.ScheduleType;
import io.airbyte.config.StandardSync.Status;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity.ScheduleRetrieverInput;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity.ScheduleRetrieverOutput;
import java.io.IOException;
import java.time.Instant;
import java.util.Calendar;
import java.util.Optional;
import java.util.TimeZone;
import java.util.UUID;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class ConfigFetchActivityTest {

  @Mock
  private ConfigRepository mConfigRepository;

  @Mock
  private JobPersistence mJobPersistence;

  @Mock
  private Configs mConfigs;

  @Mock
  private Job mJob;

  private ConfigFetchActivity configFetchActivity;

  private final static UUID connectionId = UUID.randomUUID();
  private final static StandardSync standardSyncWithLegacySchedule = new StandardSync()
      .withSchedule(new Schedule()
          .withTimeUnit(Schedule.TimeUnit.MINUTES)
          .withUnits(5L))
      .withStatus(Status.ACTIVE);

  private final static StandardSync standardSyncWithManualScheduleType = new StandardSync()
      .withScheduleType(ScheduleType.MANUAL)
      .withStatus(Status.ACTIVE);

  private final static StandardSync standardSyncWithBasicScheduleType = new StandardSync()
      .withScheduleType(ScheduleType.BASIC_SCHEDULE)
      .withStatus(Status.ACTIVE)
      .withScheduleData(new ScheduleData()
          .withBasicSchedule(new BasicSchedule()
              .withTimeUnit(BasicSchedule.TimeUnit.MINUTES)
              .withUnits(5L)));

  private final static StandardSync standardSyncWithCronScheduleType = new StandardSync()
      .withScheduleType(ScheduleType.CRON)
      .withStatus(Status.ACTIVE)
      .withScheduleData(new ScheduleData()
          .withCron(new Cron()
              .withCronExpression("0 0 12 * * ?")
              .withCronTimeZone("UTC")));

  private final static StandardSync standardSyncWithScheduleDisable = new StandardSync()
      .withSchedule(new Schedule()
          .withTimeUnit(Schedule.TimeUnit.MINUTES)
          .withUnits(5L))
      .withStatus(Status.INACTIVE);

  private final static StandardSync standardSyncWithScheduleDeleted = new StandardSync()
      .withSchedule(new Schedule()
          .withTimeUnit(Schedule.TimeUnit.MINUTES)
          .withUnits(5L))
      .withStatus(Status.DEPRECATED);
  private static final StandardSync standardSyncWithoutSchedule = new StandardSync();

  @Nested
  class TimeToWaitTest {

    @Test
    @DisplayName("Test that the job gets scheduled if it is not manual and if it is the first run with legacy schedule schema")
    void testFirstJobNonManual() throws IOException, JsonValidationException, ConfigNotFoundException {
      configFetchActivity = new ConfigFetchActivityImpl(mConfigRepository, mJobPersistence, mConfigs, () -> Instant.now().getEpochSecond());
      Mockito.when(mJobPersistence.getLastReplicationJob(connectionId))
          .thenReturn(Optional.empty());

      Mockito.when(mConfigRepository.getStandardSync(connectionId))
          .thenReturn(standardSyncWithLegacySchedule);

      final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

      final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

      Assertions.assertThat(output.getTimeToWait())
          .isZero();
    }

    @Test
    @DisplayName("Test that the job will wait for a long time if it is manual in the legacy schedule schema")
    void testManual() throws IOException, JsonValidationException, ConfigNotFoundException {
      configFetchActivity = new ConfigFetchActivityImpl(mConfigRepository, mJobPersistence, mConfigs, () -> Instant.now().getEpochSecond());

      Mockito.when(mConfigRepository.getStandardSync(connectionId))
          .thenReturn(standardSyncWithoutSchedule);

      final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

      final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

      Assertions.assertThat(output.getTimeToWait())
          .hasDays(100 * 365);
    }

    @Test
    @DisplayName("Test that the job will wait for a long time if it is disabled")
    void testDisable() throws IOException, JsonValidationException, ConfigNotFoundException {
      configFetchActivity = new ConfigFetchActivityImpl(mConfigRepository, mJobPersistence, mConfigs, () -> Instant.now().getEpochSecond());

      Mockito.when(mConfigRepository.getStandardSync(connectionId))
          .thenReturn(standardSyncWithScheduleDisable);

      final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

      final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

      Assertions.assertThat(output.getTimeToWait())
          .hasDays(100 * 365);
    }

    @Test
    @DisplayName("Test that the connection will wait for a long time if it is deleted")
    void testDeleted() throws IOException, JsonValidationException, ConfigNotFoundException {
      configFetchActivity = new ConfigFetchActivityImpl(mConfigRepository, mJobPersistence, mConfigs, () -> Instant.now().getEpochSecond());

      Mockito.when(mConfigRepository.getStandardSync(connectionId))
          .thenReturn(standardSyncWithScheduleDeleted);

      final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

      final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

      Assertions.assertThat(output.getTimeToWait())
          .hasDays(100 * 365);
    }

    @Test
    @DisplayName("Test we will wait the required amount of time with legacy config")
    void testWait() throws IOException, JsonValidationException, ConfigNotFoundException {
      configFetchActivity = new ConfigFetchActivityImpl(mConfigRepository, mJobPersistence, mConfigs, () -> 60L * 3);

      Mockito.when(mJob.getStartedAtInSecond())
          .thenReturn(Optional.of(60L));

      Mockito.when(mJobPersistence.getLastReplicationJob(connectionId))
          .thenReturn(Optional.of(mJob));

      Mockito.when(mConfigRepository.getStandardSync(connectionId))
          .thenReturn(standardSyncWithLegacySchedule);

      final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

      final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

      Assertions.assertThat(output.getTimeToWait())
          .hasMinutes(3);
    }

    @Test
    @DisplayName("Test we will not wait if we are late in the legacy schedule schema")
    void testNotWaitIfLate() throws IOException, JsonValidationException, ConfigNotFoundException {
      configFetchActivity = new ConfigFetchActivityImpl(mConfigRepository, mJobPersistence, mConfigs, () -> 60L * 10);

      Mockito.when(mJob.getStartedAtInSecond())
          .thenReturn(Optional.of(60L));

      Mockito.when(mJobPersistence.getLastReplicationJob(connectionId))
          .thenReturn(Optional.of(mJob));

      Mockito.when(mConfigRepository.getStandardSync(connectionId))
          .thenReturn(standardSyncWithLegacySchedule);

      final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

      final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

      Assertions.assertThat(output.getTimeToWait())
          .isZero();
    }

  }

  @Test
  @DisplayName("Test that the job will wait a long time if it is MANUAL scheduleType")
  void testManualScheduleType() throws IOException, JsonValidationException, ConfigNotFoundException {
    configFetchActivity = new ConfigFetchActivityImpl(mConfigRepository, mJobPersistence, mConfigs, () -> Instant.now().getEpochSecond());

    Mockito.when(mConfigRepository.getStandardSync(connectionId))
        .thenReturn(standardSyncWithManualScheduleType);

    final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

    final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

    Assertions.assertThat(output.getTimeToWait())
        .hasDays(100 * 365);
  }

  @Test
  @DisplayName("Test that the job will be immediately scheduled if it is a BASIC_SCHEDULE type on the first run")
  void testBasicScheduleTypeFirstRun() throws IOException, JsonValidationException, ConfigNotFoundException {
    configFetchActivity = new ConfigFetchActivityImpl(mConfigRepository, mJobPersistence, mConfigs, () -> Instant.now().getEpochSecond());
    Mockito.when(mJobPersistence.getLastReplicationJob(connectionId))
        .thenReturn(Optional.empty());

    Mockito.when(mConfigRepository.getStandardSync(connectionId))
        .thenReturn(standardSyncWithBasicScheduleType);

    final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

    final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

    Assertions.assertThat(output.getTimeToWait())
        .isZero();
  }

  @Test
  @DisplayName("Test that we will wait the required amount of time with a BASIC_SCHEDULE type on a subsequent run")
  void testBasicScheduleSubsequentRun() throws IOException, JsonValidationException, ConfigNotFoundException {
    configFetchActivity = new ConfigFetchActivityImpl(mConfigRepository, mJobPersistence, mConfigs, () -> 60L * 3);

    Mockito.when(mJob.getStartedAtInSecond())
        .thenReturn(Optional.of(60L));

    Mockito.when(mJobPersistence.getLastReplicationJob(connectionId))
        .thenReturn(Optional.of(mJob));

    Mockito.when(mConfigRepository.getStandardSync(connectionId))
        .thenReturn(standardSyncWithBasicScheduleType);

    final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

    final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

    Assertions.assertThat(output.getTimeToWait())
        .hasMinutes(3);
  }

  @Test
  @DisplayName("Test that the job will wait to be scheduled if it is a CRON type")
  void testCronScheduleSubsequentRun() throws IOException, JsonValidationException, ConfigNotFoundException {
    Calendar mockRightNow = Calendar.getInstance(TimeZone.getTimeZone("UTC"));
    mockRightNow.set(Calendar.HOUR_OF_DAY, 0);
    mockRightNow.set(Calendar.MINUTE, 0);
    mockRightNow.set(Calendar.SECOND, 0);
    mockRightNow.set(Calendar.MILLISECOND, 0);
    configFetchActivity = new ConfigFetchActivityImpl(mConfigRepository, mJobPersistence, mConfigs, () -> mockRightNow.getTimeInMillis() / 1000L);

    Mockito.when(mJobPersistence.getLastReplicationJob(connectionId))
        .thenReturn(Optional.of(mJob));

    Mockito.when(mConfigRepository.getStandardSync(connectionId))
        .thenReturn(standardSyncWithCronScheduleType);

    final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

    final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

    Assertions.assertThat(output.getTimeToWait())
        .hasHours(12);
  }

  @Test
  @DisplayName("Test that the job will only be scheduled once per minimum cron interval")
  void testCronScheduleMinimumInterval() throws IOException, JsonValidationException, ConfigNotFoundException {
    Calendar mockRightNow = Calendar.getInstance(TimeZone.getTimeZone("UTC"));
    mockRightNow.set(Calendar.HOUR_OF_DAY, 12);
    mockRightNow.set(Calendar.MINUTE, 0);
    mockRightNow.set(Calendar.SECOND, 0);
    mockRightNow.set(Calendar.MILLISECOND, 0);
    configFetchActivity = new ConfigFetchActivityImpl(mConfigRepository, mJobPersistence, mConfigs, () -> mockRightNow.getTimeInMillis() / 1000L);

    Mockito.when(mJob.getStartedAtInSecond()).thenReturn(Optional.of(mockRightNow.getTimeInMillis() / 1000L));
    Mockito.when(mJobPersistence.getLastReplicationJob(connectionId))
        .thenReturn(Optional.of(mJob));

    Mockito.when(mConfigRepository.getStandardSync(connectionId))
        .thenReturn(standardSyncWithCronScheduleType);

    final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

    final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

    Assertions.assertThat(output.getTimeToWait())
        .hasHours(24);
  }

  @Nested
  class TestGetMaxAttempt {

    @Test
    @DisplayName("Test that we are using to right service to get the maximum amout of attempt")
    void testGetMaxAttempt() {
      final int maxAttempt = 15031990;
      Mockito.when(mConfigs.getSyncJobMaxAttempts())
          .thenReturn(15031990);

      configFetchActivity = new ConfigFetchActivityImpl(mConfigRepository, mJobPersistence, mConfigs, () -> Instant.now().getEpochSecond());

      Assertions.assertThat(configFetchActivity.getMaxAttempt().getMaxAttempt())
          .isEqualTo(maxAttempt);
    }

  }

}
