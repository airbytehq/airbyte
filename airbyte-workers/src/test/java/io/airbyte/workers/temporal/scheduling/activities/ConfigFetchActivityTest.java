/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.config.Configs;
import io.airbyte.config.Schedule;
import io.airbyte.config.Schedule.TimeUnit;
import io.airbyte.config.StandardSync;
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
import java.util.Optional;
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
public class ConfigFetchActivityTest {

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
  private final static StandardSync standardSyncWithSchedule = new StandardSync()
      .withSchedule(new Schedule()
          .withTimeUnit(TimeUnit.MINUTES)
          .withUnits(5L))
      .withStatus(Status.ACTIVE);

  private final static StandardSync standardSyncWithScheduleDisable = new StandardSync()
      .withSchedule(new Schedule()
          .withTimeUnit(TimeUnit.MINUTES)
          .withUnits(5L))
      .withStatus(Status.INACTIVE);

  private final static StandardSync standardSyncWithScheduleDeleted = new StandardSync()
      .withSchedule(new Schedule()
          .withTimeUnit(TimeUnit.MINUTES)
          .withUnits(5L))
      .withStatus(Status.DEPRECATED);
  private static final StandardSync standardSyncWithoutSchedule = new StandardSync();

  @Nested
  class TimeToWaitTest {

    @Test
    @DisplayName("Test that the job get scheduled if it is not manual and if it is the first run")
    public void testFirstJobNonManual() throws IOException, JsonValidationException, ConfigNotFoundException {
      configFetchActivity = new ConfigFetchActivityImpl(mConfigRepository, mJobPersistence, mConfigs, () -> Instant.now().getEpochSecond());
      Mockito.when(mJobPersistence.getLastReplicationJob(connectionId))
          .thenReturn(Optional.empty());

      Mockito.when(mConfigRepository.getStandardSync(connectionId))
          .thenReturn(standardSyncWithSchedule);

      final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

      final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

      Assertions.assertThat(output.getTimeToWait())
          .isZero();
    }

    @Test
    @DisplayName("Test that the job will wait for a long time if it is manual")
    public void testManual() throws IOException, JsonValidationException, ConfigNotFoundException {
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
    public void testDisable() throws IOException, JsonValidationException, ConfigNotFoundException {
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
    public void testDeleted() throws IOException, JsonValidationException, ConfigNotFoundException {
      configFetchActivity = new ConfigFetchActivityImpl(mConfigRepository, mJobPersistence, mConfigs, () -> Instant.now().getEpochSecond());

      Mockito.when(mConfigRepository.getStandardSync(connectionId))
          .thenReturn(standardSyncWithScheduleDeleted);

      final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

      final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

      Assertions.assertThat(output.getTimeToWait())
          .hasDays(100 * 365);
    }

    @Test
    @DisplayName("Test we will wait the required amount of time")
    public void testWait() throws IOException, JsonValidationException, ConfigNotFoundException {
      configFetchActivity = new ConfigFetchActivityImpl(mConfigRepository, mJobPersistence, mConfigs, () -> 60L * 3);

      Mockito.when(mJob.getStartedAtInSecond())
          .thenReturn(Optional.of(60L));

      Mockito.when(mJobPersistence.getLastReplicationJob(connectionId))
          .thenReturn(Optional.of(mJob));

      Mockito.when(mConfigRepository.getStandardSync(connectionId))
          .thenReturn(standardSyncWithSchedule);

      final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

      final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

      Assertions.assertThat(output.getTimeToWait())
          .hasMinutes(3);
    }

    @Test
    @DisplayName("Test we will not wait if we are late")
    public void testNotWaitIfLate() throws IOException, JsonValidationException, ConfigNotFoundException {
      configFetchActivity = new ConfigFetchActivityImpl(mConfigRepository, mJobPersistence, mConfigs, () -> 60L * 10);

      Mockito.when(mJob.getStartedAtInSecond())
          .thenReturn(Optional.of(60L));

      Mockito.when(mJobPersistence.getLastReplicationJob(connectionId))
          .thenReturn(Optional.of(mJob));

      Mockito.when(mConfigRepository.getStandardSync(connectionId))
          .thenReturn(standardSyncWithSchedule);

      final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

      final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

      Assertions.assertThat(output.getTimeToWait())
          .isZero();
    }

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
