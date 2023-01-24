/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

import io.airbyte.api.client.generated.ConnectionApi;
import io.airbyte.api.client.generated.JobsApi;
import io.airbyte.api.client.generated.WorkspaceApi;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.ConnectionRead;
import io.airbyte.api.client.model.generated.ConnectionSchedule;
import io.airbyte.api.client.model.generated.ConnectionScheduleData;
import io.airbyte.api.client.model.generated.ConnectionScheduleDataBasicSchedule;
import io.airbyte.api.client.model.generated.ConnectionScheduleDataBasicSchedule.TimeUnitEnum;
import io.airbyte.api.client.model.generated.ConnectionScheduleDataCron;
import io.airbyte.api.client.model.generated.ConnectionScheduleType;
import io.airbyte.api.client.model.generated.ConnectionStatus;
import io.airbyte.api.client.model.generated.JobOptionalRead;
import io.airbyte.api.client.model.generated.JobRead;
import io.airbyte.api.client.model.generated.WorkspaceRead;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity.ScheduleRetrieverInput;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity.ScheduleRetrieverOutput;
import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import java.util.Calendar;
import java.util.TimeZone;
import java.util.UUID;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class ConfigFetchActivityTest {

  private static final Integer SYNC_JOB_MAX_ATTEMPTS = 3;

  @Mock
  private JobsApi mJobsApi;

  @Mock
  private WorkspaceApi mWorkspaceApi;
  @Mock
  private JobRead mJobRead;

  @Mock
  private ConnectionApi mConnectionApi;

  private ConfigFetchActivityImpl configFetchActivity;

  private final static UUID connectionId = UUID.randomUUID();
  private final static ConnectionRead connectionReadWithLegacySchedule = new ConnectionRead()
      .schedule(new ConnectionSchedule()
          .timeUnit(ConnectionSchedule.TimeUnitEnum.MINUTES)
          .units(5L))
      .status(ConnectionStatus.ACTIVE);

  private final static ConnectionRead connectionReadWithManualScheduleType = new ConnectionRead()
      .scheduleType(ConnectionScheduleType.MANUAL)
      .status(ConnectionStatus.ACTIVE);

  private final static ConnectionRead connectionReadWithBasicScheduleType = new ConnectionRead()
      .scheduleType(ConnectionScheduleType.BASIC)
      .status(ConnectionStatus.ACTIVE)
      .scheduleData(new ConnectionScheduleData()
          .basicSchedule(new ConnectionScheduleDataBasicSchedule()
              .timeUnit(TimeUnitEnum.MINUTES)
              .units(5L)));

  public static final String UTC = "UTC";
  private final static ConnectionRead connectionReadWithCronScheduleType = new ConnectionRead()
      .scheduleType(ConnectionScheduleType.CRON)
      .status(ConnectionStatus.ACTIVE)
      .scheduleData(new ConnectionScheduleData()
          .cron(new ConnectionScheduleDataCron()
              .cronExpression("0 0 12 * * ?")
              .cronTimeZone(UTC)));

  private final static ConnectionRead connectionReadWithScheduleDisable = new ConnectionRead()
      .schedule(new ConnectionSchedule()
          .timeUnit(ConnectionSchedule.TimeUnitEnum.MINUTES)
          .units(5L))
      .status(ConnectionStatus.INACTIVE);

  private final static ConnectionRead connectionReadWithScheduleDeleted = new ConnectionRead()
      .schedule(new ConnectionSchedule()
          .timeUnit(ConnectionSchedule.TimeUnitEnum.MINUTES)
          .units(5L))
      .status(ConnectionStatus.DEPRECATED);
  private static final ConnectionRead connectionReadWithoutSchedule = new ConnectionRead();

  @BeforeEach
  void setup() {
    configFetchActivity =
        new ConfigFetchActivityImpl(mJobsApi, mWorkspaceApi, SYNC_JOB_MAX_ATTEMPTS,
            () -> Instant.now().getEpochSecond(), mConnectionApi);
  }

  @Nested
  class TimeToWaitTest {

    @Test
    @DisplayName("Test that the job gets scheduled if it is not manual and if it is the first run with legacy schedule schema")
    void testFirstJobNonManual() throws IOException, JsonValidationException, ConfigNotFoundException, ApiException {
      when(mJobsApi.getLastReplicationJob(any()))
          .thenReturn(new JobOptionalRead());

      when(mConnectionApi.getConnection(any()))
          .thenReturn(connectionReadWithLegacySchedule);

      final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

      final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

      Assertions.assertThat(output.getTimeToWait())
          .isZero();
    }

    @Test
    @DisplayName("Test that the job will wait for a long time if it is manual in the legacy schedule schema")
    void testManual() throws ApiException {
      when(mConnectionApi.getConnection(any()))
          .thenReturn(connectionReadWithoutSchedule);

      final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

      final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

      Assertions.assertThat(output.getTimeToWait())
          .hasDays(100 * 365);
    }

    @Test
    @DisplayName("Test that the job will wait for a long time if it is disabled")
    void testDisable() throws ApiException {
      when(mConnectionApi.getConnection(any()))
          .thenReturn(connectionReadWithScheduleDisable);

      final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

      final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

      Assertions.assertThat(output.getTimeToWait())
          .hasDays(100 * 365);
    }

    @Test
    @DisplayName("Test that the connection will wait for a long time if it is deleted")
    void testDeleted() throws ApiException {
      when(mConnectionApi.getConnection(any()))
          .thenReturn(connectionReadWithScheduleDeleted);

      final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

      final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

      Assertions.assertThat(output.getTimeToWait())
          .hasDays(100 * 365);
    }

    @Test
    @DisplayName("Test we will wait the required amount of time with legacy config")
    void testWait() throws IOException, JsonValidationException, ConfigNotFoundException, ApiException {
      configFetchActivity =
          new ConfigFetchActivityImpl(mJobsApi, mWorkspaceApi, SYNC_JOB_MAX_ATTEMPTS, () -> 60L * 3, mConnectionApi);

      when(mJobRead.getStartedAt())
          .thenReturn(60L);

      when(mJobsApi.getLastReplicationJob(any()))
          .thenReturn(new JobOptionalRead().job(mJobRead));

      when(mConnectionApi.getConnection(any()))
          .thenReturn(connectionReadWithLegacySchedule);

      final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

      final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

      Assertions.assertThat(output.getTimeToWait())
          .hasMinutes(3);
    }

    @Test
    @DisplayName("Test we will not wait if we are late in the legacy schedule schema")
    void testNotWaitIfLate() throws IOException, ApiException {
      configFetchActivity =
          new ConfigFetchActivityImpl(mJobsApi, mWorkspaceApi, SYNC_JOB_MAX_ATTEMPTS, () -> 60L * 10, mConnectionApi);

      when(mJobRead.getStartedAt())
          .thenReturn(60L);

      when(mJobsApi.getLastReplicationJob(any()))
          .thenReturn(new JobOptionalRead().job(mJobRead));

      when(mConnectionApi.getConnection(any()))
          .thenReturn(connectionReadWithLegacySchedule);

      final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

      final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

      Assertions.assertThat(output.getTimeToWait())
          .isZero();
    }

  }

  @Test
  @DisplayName("Test that the job will wait a long time if it is MANUAL scheduleType")
  void testManualScheduleType() throws ApiException {
    when(mConnectionApi.getConnection(any()))
        .thenReturn(connectionReadWithManualScheduleType);

    final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

    final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

    Assertions.assertThat(output.getTimeToWait())
        .hasDays(100 * 365);
  }

  @Test
  @DisplayName("Test that the job will be immediately scheduled if it is a BASIC_SCHEDULE type on the first run")
  void testBasicScheduleTypeFirstRun() throws IOException, ApiException {
    when(mJobsApi.getLastReplicationJob(any()))
        .thenReturn(new JobOptionalRead());

    when(mConnectionApi.getConnection(any()))
        .thenReturn(connectionReadWithBasicScheduleType);

    final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

    final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

    Assertions.assertThat(output.getTimeToWait())
        .isZero();
  }

  @Test
  @DisplayName("Test that we will wait the required amount of time with a BASIC_SCHEDULE type on a subsequent run")
  void testBasicScheduleSubsequentRun() throws IOException, ApiException {
    configFetchActivity = new ConfigFetchActivityImpl(mJobsApi, mWorkspaceApi, SYNC_JOB_MAX_ATTEMPTS, () -> 60L * 3, mConnectionApi);

    when(mJobRead.getStartedAt())
        .thenReturn(60L);

    when(mJobsApi.getLastReplicationJob(any()))
        .thenReturn(new JobOptionalRead().job(mJobRead));

    when(mConnectionApi.getConnection(any()))
        .thenReturn(connectionReadWithBasicScheduleType);

    final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

    final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

    Assertions.assertThat(output.getTimeToWait())
        .hasMinutes(3);
  }

  @Test
  @DisplayName("Test that the job will wait to be scheduled if it is a CRON type")
  void testCronScheduleSubsequentRun() throws IOException, JsonValidationException, ConfigNotFoundException, ApiException {
    final Calendar mockRightNow = Calendar.getInstance(TimeZone.getTimeZone(UTC));
    mockRightNow.set(Calendar.HOUR_OF_DAY, 0);
    mockRightNow.set(Calendar.MINUTE, 0);
    mockRightNow.set(Calendar.SECOND, 0);
    mockRightNow.set(Calendar.MILLISECOND, 0);

    when(mWorkspaceApi.getWorkspaceByConnectionId(any())).thenReturn(new WorkspaceRead().workspaceId(UUID.randomUUID()));

    configFetchActivity =
        new ConfigFetchActivityImpl(mJobsApi, mWorkspaceApi, SYNC_JOB_MAX_ATTEMPTS,
            () -> mockRightNow.getTimeInMillis() / 1000L, mConnectionApi);

    when(mJobsApi.getLastReplicationJob(any()))
        .thenReturn(new JobOptionalRead().job(mJobRead));

    when(mConnectionApi.getConnection(any()))
        .thenReturn(connectionReadWithCronScheduleType);

    final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

    final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

    Assertions.assertThat(output.getTimeToWait())
        .hasHours(12);
  }

  @Test
  @DisplayName("Test that the job will only be scheduled once per minimum cron interval")
  void testCronScheduleMinimumInterval() throws IOException, JsonValidationException, ConfigNotFoundException, ApiException {
    final Calendar mockRightNow = Calendar.getInstance(TimeZone.getTimeZone(UTC));
    mockRightNow.set(Calendar.HOUR_OF_DAY, 12);
    mockRightNow.set(Calendar.MINUTE, 0);
    mockRightNow.set(Calendar.SECOND, 0);
    mockRightNow.set(Calendar.MILLISECOND, 0);

    when(mWorkspaceApi.getWorkspaceByConnectionId(any())).thenReturn(new WorkspaceRead().workspaceId(UUID.randomUUID()));

    configFetchActivity =
        new ConfigFetchActivityImpl(mJobsApi, mWorkspaceApi, SYNC_JOB_MAX_ATTEMPTS,
            () -> mockRightNow.getTimeInMillis() / 1000L, mConnectionApi);

    when(mJobRead.getStartedAt()).thenReturn(mockRightNow.getTimeInMillis() / 1000L);
    when(mJobsApi.getLastReplicationJob(any()))
        .thenReturn(new JobOptionalRead().job(mJobRead));

    when(mConnectionApi.getConnection(any()))
        .thenReturn(connectionReadWithCronScheduleType);

    final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

    final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

    Assertions.assertThat(output.getTimeToWait())
        .hasHours(24);
  }

  @Test
  @DisplayName("Test that for specific workspace ids, we add some noise in the cron scheduling")
  void testCronSchedulingNoise() throws IOException, JsonValidationException, ConfigNotFoundException, ApiException {
    final Calendar mockRightNow = Calendar.getInstance(TimeZone.getTimeZone(UTC));
    mockRightNow.set(Calendar.HOUR_OF_DAY, 0);
    mockRightNow.set(Calendar.MINUTE, 0);
    mockRightNow.set(Calendar.SECOND, 0);
    mockRightNow.set(Calendar.MILLISECOND, 0);

    when(mWorkspaceApi.getWorkspaceByConnectionId(any()))
        .thenReturn(new WorkspaceRead().workspaceId(UUID.fromString("226edbc1-4a9c-4401-95a9-90435d667d9d")));

    configFetchActivity =
        new ConfigFetchActivityImpl(mJobsApi, mWorkspaceApi, SYNC_JOB_MAX_ATTEMPTS,
            () -> mockRightNow.getTimeInMillis() / 1000L, mConnectionApi);

    when(mJobRead.getStartedAt()).thenReturn(mockRightNow.getTimeInMillis() / 1000L);
    when(mJobsApi.getLastReplicationJob(any()))
        .thenReturn(new JobOptionalRead().job(mJobRead));

    when(mConnectionApi.getConnection(any()))
        .thenReturn(connectionReadWithCronScheduleType);

    final ScheduleRetrieverInput input = new ScheduleRetrieverInput(connectionId);

    final ScheduleRetrieverOutput output = configFetchActivity.getTimeToWait(input);

    // Note: compareTo returns positive if the left side is greater than the right.
    Assertions.assertThat(output.getTimeToWait().compareTo(Duration.ofHours(12)) > 0).isTrue();
  }

  @Nested
  class TestGetMaxAttempt {

    @Test
    @DisplayName("Test that we are using to right service to get the maximum amount of attempt")
    void testGetMaxAttempt() {
      final int maxAttempt = 15031990;
      configFetchActivity =
          new ConfigFetchActivityImpl(mJobsApi, mWorkspaceApi, maxAttempt, () -> Instant.now().getEpochSecond(), mConnectionApi);
      Assertions.assertThat(configFetchActivity.getMaxAttempt().getMaxAttempt())
          .isEqualTo(maxAttempt);
    }

  }

}
