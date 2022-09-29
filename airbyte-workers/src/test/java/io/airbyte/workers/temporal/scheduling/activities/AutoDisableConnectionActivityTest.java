/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static io.airbyte.config.EnvConfigs.DEFAULT_DAYS_OF_ONLY_FAILED_JOBS_BEFORE_CONNECTION_DISABLE;
import static io.airbyte.config.EnvConfigs.DEFAULT_FAILED_JOBS_IN_A_ROW_BEFORE_CONNECTION_DISABLE;
import static io.airbyte.persistence.job.models.Job.REPLICATION_TYPES;
import static org.assertj.core.api.AssertionsForClassTypes.assertThat;

import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.Status;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.persistence.job.JobNotifier;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.persistence.job.models.Job;
import io.airbyte.persistence.job.models.JobStatus;
import io.airbyte.persistence.job.models.JobWithStatusAndTimestamp;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.temporal.scheduling.activities.AutoDisableConnectionActivity.AutoDisableConnectionActivityInput;
import io.airbyte.workers.temporal.scheduling.activities.AutoDisableConnectionActivity.AutoDisableConnectionOutput;
import java.io.IOException;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class AutoDisableConnectionActivityTest {

  @Mock
  private FeatureFlags mFeatureFlags;

  @Mock
  private ConfigRepository mConfigRepository;

  @Mock
  private JobPersistence mJobPersistence;

  @Mock
  private JobNotifier mJobNotifier;

  @Mock
  private Job mJob;

  private AutoDisableConnectionActivityImpl autoDisableActivity;

  private static final UUID CONNECTION_ID = UUID.randomUUID();
  private static final Instant CURR_INSTANT = Instant.now();
  private static final AutoDisableConnectionActivityInput ACTIVITY_INPUT = new AutoDisableConnectionActivityInput(CONNECTION_ID, CURR_INSTANT);
  private static final int MAX_FAILURE_JOBS_IN_A_ROW = DEFAULT_FAILED_JOBS_IN_A_ROW_BEFORE_CONNECTION_DISABLE;
  private static final int MAX_DAYS_OF_ONLY_FAILED_JOBS = DEFAULT_DAYS_OF_ONLY_FAILED_JOBS_BEFORE_CONNECTION_DISABLE;
  private static final int MAX_DAYS_OF_ONLY_FAILED_JOBS_BEFORE_WARNING = DEFAULT_DAYS_OF_ONLY_FAILED_JOBS_BEFORE_CONNECTION_DISABLE / 2;

  private static final JobWithStatusAndTimestamp FAILED_JOB =
      new JobWithStatusAndTimestamp(1, JobStatus.FAILED, CURR_INSTANT.getEpochSecond(), CURR_INSTANT.getEpochSecond());
  private static final JobWithStatusAndTimestamp SUCCEEDED_JOB =
      new JobWithStatusAndTimestamp(1, JobStatus.SUCCEEDED, CURR_INSTANT.getEpochSecond(), CURR_INSTANT.getEpochSecond());
  private static final JobWithStatusAndTimestamp CANCELLED_JOB =
      new JobWithStatusAndTimestamp(1, JobStatus.CANCELLED, CURR_INSTANT.getEpochSecond(), CURR_INSTANT.getEpochSecond());

  private final StandardSync standardSync = new StandardSync();

  @BeforeEach
  void setUp() throws IOException, JsonValidationException, ConfigNotFoundException {
    Mockito.when(mConfigRepository.getStandardSync(CONNECTION_ID)).thenReturn(standardSync);
    standardSync.setStatus(Status.ACTIVE);
    Mockito.when(mFeatureFlags.autoDisablesFailingConnections()).thenReturn(true);
    Mockito.when(mJobPersistence.getLastReplicationJob(CONNECTION_ID)).thenReturn(Optional.of(mJob));
    Mockito.when(mJobPersistence.getFirstReplicationJob(CONNECTION_ID)).thenReturn(Optional.of(mJob));

    autoDisableActivity = new AutoDisableConnectionActivityImpl(mConfigRepository, mJobPersistence, mFeatureFlags, MAX_DAYS_OF_ONLY_FAILED_JOBS,
        MAX_FAILURE_JOBS_IN_A_ROW, mJobNotifier);
  }

  // test warnings

  @Test
  @DisplayName("Test that a notification warning is sent for connections that have failed `MAX_FAILURE_JOBS_IN_A_ROW / 2` times")
  void testWarningNotificationsForAutoDisablingMaxNumFailures() throws IOException {

    // from most recent to least recent: MAX_FAILURE_JOBS_IN_A_ROW/2 and 1 success
    final List<JobWithStatusAndTimestamp> jobs = new ArrayList<>(Collections.nCopies(MAX_FAILURE_JOBS_IN_A_ROW / 2, FAILED_JOB));
    jobs.add(SUCCEEDED_JOB);

    Mockito.when(mJobPersistence.listJobStatusAndTimestampWithConnection(CONNECTION_ID, REPLICATION_TYPES,
        CURR_INSTANT.minus(MAX_DAYS_OF_ONLY_FAILED_JOBS, ChronoUnit.DAYS))).thenReturn(jobs);

    final AutoDisableConnectionOutput output = autoDisableActivity.autoDisableFailingConnection(ACTIVITY_INPUT);
    assertThat(output.isDisabled()).isFalse();
    assertThat(standardSync.getStatus()).isEqualTo(Status.ACTIVE);
    Mockito.verify(mJobNotifier, Mockito.never()).autoDisableConnection(Mockito.any());
    Mockito.verify(mJobNotifier, Mockito.times(1)).autoDisableConnectionWarning(Mockito.any());
  }

  @Test
  @DisplayName("Test that a notification warning is sent after only failed jobs in last `MAX_DAYS_OF_STRAIGHT_FAILURE / 2` days")
  void testWarningNotificationsForAutoDisablingMaxDaysOfFailure() throws IOException {
    Mockito.when(mJobPersistence.listJobStatusAndTimestampWithConnection(CONNECTION_ID, REPLICATION_TYPES,
        CURR_INSTANT.minus(MAX_DAYS_OF_ONLY_FAILED_JOBS, ChronoUnit.DAYS)))
        .thenReturn(Collections.singletonList(FAILED_JOB));

    Mockito.when(mJob.getCreatedAtInSecond()).thenReturn(
        CURR_INSTANT.getEpochSecond() - TimeUnit.DAYS.toSeconds(MAX_DAYS_OF_ONLY_FAILED_JOBS_BEFORE_WARNING));

    final AutoDisableConnectionOutput output = autoDisableActivity.autoDisableFailingConnection(ACTIVITY_INPUT);
    assertThat(output.isDisabled()).isFalse();
    assertThat(standardSync.getStatus()).isEqualTo(Status.ACTIVE);
    Mockito.verify(mJobNotifier, Mockito.never()).autoDisableConnection(Mockito.any());
    Mockito.verify(mJobNotifier, Mockito.times(1)).autoDisableConnectionWarning(Mockito.any());
  }

  @Test
  @DisplayName("Test that a notification warning is not sent after one was just sent for failing multiple days")
  void testWarningNotificationsDoesNotSpam() throws IOException {
    final List<JobWithStatusAndTimestamp> jobs = new ArrayList<>(Collections.nCopies(2, FAILED_JOB));
    final long mJobCreateOrUpdatedInSeconds = CURR_INSTANT.getEpochSecond() - TimeUnit.DAYS.toSeconds(MAX_DAYS_OF_ONLY_FAILED_JOBS_BEFORE_WARNING);

    Mockito.when(mJobPersistence.listJobStatusAndTimestampWithConnection(CONNECTION_ID, REPLICATION_TYPES,
        CURR_INSTANT.minus(MAX_DAYS_OF_ONLY_FAILED_JOBS, ChronoUnit.DAYS))).thenReturn(jobs);

    Mockito.when(mJob.getCreatedAtInSecond()).thenReturn(mJobCreateOrUpdatedInSeconds);
    Mockito.when(mJob.getUpdatedAtInSecond()).thenReturn(mJobCreateOrUpdatedInSeconds);

    final AutoDisableConnectionOutput output = autoDisableActivity.autoDisableFailingConnection(ACTIVITY_INPUT);
    assertThat(output.isDisabled()).isFalse();
    assertThat(standardSync.getStatus()).isEqualTo(Status.ACTIVE);
    Mockito.verify(mJobNotifier, Mockito.never()).autoDisableConnection(Mockito.any());
    Mockito.verify(mJobNotifier, Mockito.never()).autoDisableConnectionWarning(Mockito.any());
  }

  @Test
  @DisplayName("Test that a notification warning is not sent after one was just sent for consecutive failures")
  void testWarningNotificationsDoesNotSpamAfterConsecutiveFailures() throws IOException {
    final List<JobWithStatusAndTimestamp> jobs = new ArrayList<>(Collections.nCopies(MAX_FAILURE_JOBS_IN_A_ROW - 1, FAILED_JOB));
    final long mJobCreateOrUpdatedInSeconds = CURR_INSTANT.getEpochSecond() - TimeUnit.DAYS.toSeconds(MAX_DAYS_OF_ONLY_FAILED_JOBS_BEFORE_WARNING);

    Mockito.when(mJobPersistence.listJobStatusAndTimestampWithConnection(CONNECTION_ID, REPLICATION_TYPES,
        CURR_INSTANT.minus(MAX_DAYS_OF_ONLY_FAILED_JOBS, ChronoUnit.DAYS))).thenReturn(jobs);

    Mockito.when(mJob.getCreatedAtInSecond()).thenReturn(mJobCreateOrUpdatedInSeconds);
    Mockito.when(mJob.getUpdatedAtInSecond()).thenReturn(mJobCreateOrUpdatedInSeconds);

    final AutoDisableConnectionOutput output = autoDisableActivity.autoDisableFailingConnection(ACTIVITY_INPUT);
    assertThat(output.isDisabled()).isFalse();
    assertThat(standardSync.getStatus()).isEqualTo(Status.ACTIVE);
    Mockito.verify(mJobNotifier, Mockito.never()).autoDisableConnection(Mockito.any());
    Mockito.verify(mJobNotifier, Mockito.never()).autoDisableConnectionWarning(Mockito.any());
  }

  @Test
  @DisplayName("Test that the connection is _not_ disabled and no warning is sent after only failed jobs and oldest job is less than `MAX_DAYS_OF_STRAIGHT_FAILURE / 2 `days old")
  void testOnlyFailuresButFirstJobYoungerThanMaxDaysWarning() throws IOException {
    Mockito.when(mJobPersistence.listJobStatusAndTimestampWithConnection(CONNECTION_ID, REPLICATION_TYPES,
        CURR_INSTANT.minus(MAX_DAYS_OF_ONLY_FAILED_JOBS, ChronoUnit.DAYS)))
        .thenReturn(Collections.singletonList(FAILED_JOB));

    Mockito.when(mJob.getCreatedAtInSecond()).thenReturn(CURR_INSTANT.getEpochSecond());

    final AutoDisableConnectionOutput output = autoDisableActivity.autoDisableFailingConnection(ACTIVITY_INPUT);
    assertThat(output.isDisabled()).isFalse();
    assertThat(standardSync.getStatus()).isEqualTo(Status.ACTIVE);
    Mockito.verify(mJobNotifier, Mockito.never()).autoDisableConnection(Mockito.any());
    Mockito.verify(mJobNotifier, Mockito.never()).autoDisableConnectionWarning(Mockito.any());
  }

  // test should disable / shouldn't disable cases

  @Test
  @DisplayName("Test that the connection is disabled after MAX_FAILURE_JOBS_IN_A_ROW straight failures")
  void testMaxFailuresInARow() throws IOException, JsonValidationException, ConfigNotFoundException {
    // from most recent to least recent: MAX_FAILURE_JOBS_IN_A_ROW and 1 success
    final List<JobWithStatusAndTimestamp> jobs = new ArrayList<>(Collections.nCopies(MAX_FAILURE_JOBS_IN_A_ROW, FAILED_JOB));
    jobs.add(SUCCEEDED_JOB);

    Mockito.when(mJobPersistence.listJobStatusAndTimestampWithConnection(CONNECTION_ID, REPLICATION_TYPES,
        CURR_INSTANT.minus(MAX_DAYS_OF_ONLY_FAILED_JOBS, ChronoUnit.DAYS))).thenReturn(jobs);
    Mockito.when(mConfigRepository.getStandardSync(CONNECTION_ID)).thenReturn(standardSync);

    final AutoDisableConnectionOutput output = autoDisableActivity.autoDisableFailingConnection(ACTIVITY_INPUT);
    assertThat(output.isDisabled()).isTrue();
    assertThat(standardSync.getStatus()).isEqualTo(Status.INACTIVE);
    Mockito.verify(mJobNotifier, Mockito.never()).autoDisableConnectionWarning(Mockito.any());
    Mockito.verify(mJobNotifier, Mockito.times(1)).autoDisableConnection(Mockito.any());
  }

  @Test
  @DisplayName("Test that the connection is _not_ disabled after MAX_FAILURE_JOBS_IN_A_ROW - 1 straight failures")
  void testLessThanMaxFailuresInARow() throws IOException {
    // from most recent to least recent: MAX_FAILURE_JOBS_IN_A_ROW-1 and 1 success
    final List<JobWithStatusAndTimestamp> jobs = new ArrayList<>(Collections.nCopies(MAX_FAILURE_JOBS_IN_A_ROW - 1, FAILED_JOB));
    jobs.add(SUCCEEDED_JOB);

    Mockito.when(mJobPersistence.listJobStatusAndTimestampWithConnection(CONNECTION_ID, REPLICATION_TYPES,
        CURR_INSTANT.minus(MAX_DAYS_OF_ONLY_FAILED_JOBS, ChronoUnit.DAYS))).thenReturn(jobs);
    Mockito.when(mJob.getCreatedAtInSecond()).thenReturn(
        CURR_INSTANT.getEpochSecond() - TimeUnit.DAYS.toSeconds(MAX_DAYS_OF_ONLY_FAILED_JOBS));

    final AutoDisableConnectionOutput output = autoDisableActivity.autoDisableFailingConnection(ACTIVITY_INPUT);
    assertThat(output.isDisabled()).isFalse();
    assertThat(standardSync.getStatus()).isEqualTo(Status.ACTIVE);

    // check that no notification has been sent
    Mockito.verify(mJobNotifier, Mockito.never()).autoDisableConnection(Mockito.any());
    Mockito.verify(mJobNotifier, Mockito.never()).autoDisableConnectionWarning(Mockito.any());
  }

  @Test
  @DisplayName("Test that the connection is _not_ disabled after 0 jobs in last MAX_DAYS_OF_STRAIGHT_FAILURE days")
  void testNoRuns() throws IOException {
    Mockito.when(mJobPersistence.listJobStatusAndTimestampWithConnection(CONNECTION_ID, REPLICATION_TYPES,
        CURR_INSTANT.minus(MAX_DAYS_OF_ONLY_FAILED_JOBS, ChronoUnit.DAYS))).thenReturn(Collections.emptyList());

    final AutoDisableConnectionOutput output = autoDisableActivity.autoDisableFailingConnection(ACTIVITY_INPUT);
    assertThat(output.isDisabled()).isFalse();
    assertThat(standardSync.getStatus()).isEqualTo(Status.ACTIVE);

    Mockito.verify(mJobNotifier, Mockito.never()).autoDisableConnection(Mockito.any());
    Mockito.verify(mJobNotifier, Mockito.never()).autoDisableConnectionWarning(Mockito.any());
  }

  @Test
  @DisplayName("Test that the connection is disabled after only failed jobs in last MAX_DAYS_OF_STRAIGHT_FAILURE days")
  void testOnlyFailuresInMaxDays() throws IOException, JsonValidationException, ConfigNotFoundException {
    Mockito.when(mJobPersistence.listJobStatusAndTimestampWithConnection(CONNECTION_ID, REPLICATION_TYPES,
        CURR_INSTANT.minus(MAX_DAYS_OF_ONLY_FAILED_JOBS, ChronoUnit.DAYS)))
        .thenReturn(Collections.singletonList(FAILED_JOB));

    Mockito.when(mJob.getCreatedAtInSecond()).thenReturn(
        CURR_INSTANT.getEpochSecond() - TimeUnit.DAYS.toSeconds(MAX_DAYS_OF_ONLY_FAILED_JOBS));
    Mockito.when(mConfigRepository.getStandardSync(CONNECTION_ID)).thenReturn(standardSync);

    final AutoDisableConnectionOutput output = autoDisableActivity.autoDisableFailingConnection(ACTIVITY_INPUT);
    assertThat(output.isDisabled()).isTrue();
    assertThat(standardSync.getStatus()).isEqualTo(Status.INACTIVE);

    Mockito.verify(mJobNotifier, Mockito.times(1)).autoDisableConnection(Mockito.any());
    Mockito.verify(mJobNotifier, Mockito.never()).autoDisableConnectionWarning(Mockito.any());
  }

  @Test
  @DisplayName("Test that the connection is _not_ disabled after only cancelled jobs")
  void testIgnoreOnlyCancelledRuns() throws IOException {
    Mockito.when(mJobPersistence.listJobStatusAndTimestampWithConnection(CONNECTION_ID, REPLICATION_TYPES,
        CURR_INSTANT.minus(MAX_DAYS_OF_ONLY_FAILED_JOBS, ChronoUnit.DAYS)))
        .thenReturn(Collections.singletonList(CANCELLED_JOB));

    final AutoDisableConnectionOutput output = autoDisableActivity.autoDisableFailingConnection(ACTIVITY_INPUT);
    assertThat(output.isDisabled()).isFalse();
    assertThat(standardSync.getStatus()).isEqualTo(Status.ACTIVE);
    Mockito.verify(mJobNotifier, Mockito.never()).autoDisableConnection(Mockito.any());
    Mockito.verify(mJobNotifier, Mockito.never()).autoDisableConnectionWarning(Mockito.any());
  }

}
