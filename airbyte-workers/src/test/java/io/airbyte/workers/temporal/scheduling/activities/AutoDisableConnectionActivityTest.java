/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static io.airbyte.config.EnvConfigs.DEFAULT_FAILED_JOBS_IN_A_ROW_BEFORE_CONNECTION_DISABLE;

import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.config.Configs;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.Status;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.models.JobStatus;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.temporal.scheduling.activities.AutoDisableConnectionActivity.AutoDisableConnectionActivityInput;
import java.io.IOException;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.UUID;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
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
  private Configs mConfigs;

  @InjectMocks
  private AutoDisableConnectionActivityImpl autoDisableActivity;

  private static final UUID CONNECTION_ID = UUID.randomUUID();
  private static final Instant CURR_INSTANT = Instant.now();
  private static final AutoDisableConnectionActivityInput ACTIVITY_INPUT = new AutoDisableConnectionActivityInput(CONNECTION_ID, CURR_INSTANT);
  private static final int MAX_FAILURE_JOBS_IN_A_ROW = DEFAULT_FAILED_JOBS_IN_A_ROW_BEFORE_CONNECTION_DISABLE;

  private final StandardSync standardSync = new StandardSync();

  @BeforeEach
  void setUp() {
    standardSync.setStatus(Status.ACTIVE);
    Mockito.when(mFeatureFlags.autoDisablesFailingConnections()).thenReturn(true);
  }

  @Nested
  class AutoDisableConnectionTest {

    @Test
    @DisplayName("Test that the connection is disabled after MAX_FAILURE_JOBS_IN_A_ROW straight failures")
    public void testMaxFailuresInARow() throws IOException, JsonValidationException, ConfigNotFoundException {
      // from most recent to least recent: MAX_FAILURE_JOBS_IN_A_ROW and 1 success
      final List<JobStatus> jobStatuses = new ArrayList<>(Collections.nCopies(MAX_FAILURE_JOBS_IN_A_ROW, JobStatus.FAILED));
      jobStatuses.add(JobStatus.SUCCEEDED);

      Mockito.when(mJobPersistence.listJobStatusWithConnection(CONNECTION_ID, ConfigType.SYNC,
          CURR_INSTANT.minus(mConfigs.getMaxDaysOfOnlyFailedJobsBeforeConnectionDisable(), ChronoUnit.DAYS))).thenReturn(jobStatuses);
      Mockito.when(mConfigs.getMaxFailedJobsInARowBeforeConnectionDisable()).thenReturn(MAX_FAILURE_JOBS_IN_A_ROW);
      Mockito.when(mConfigRepository.getStandardSync(CONNECTION_ID)).thenReturn(standardSync);

      autoDisableActivity.autoDisableFailingConnection(ACTIVITY_INPUT);
      Assertions.assertThat(standardSync.getStatus()).isEqualTo(Status.INACTIVE);
    }

    @Test
    @DisplayName("Test that the connection is _not_ disabled after MAX_FAILURE_JOBS_IN_A_ROW - 1 straight failures")
    public void testLessThanMaxFailuresInARow() throws IOException {
      // from most recent to least recent: MAX_FAILURE_JOBS_IN_A_ROW-1 and 1 success
      final List<JobStatus> jobStatuses = new ArrayList<>(Collections.nCopies(MAX_FAILURE_JOBS_IN_A_ROW - 1, JobStatus.FAILED));
      jobStatuses.add(JobStatus.SUCCEEDED);

      Mockito.when(mJobPersistence.listJobStatusWithConnection(CONNECTION_ID, ConfigType.SYNC,
          CURR_INSTANT.minus(mConfigs.getMaxDaysOfOnlyFailedJobsBeforeConnectionDisable(), ChronoUnit.DAYS))).thenReturn(jobStatuses);
      Mockito.when(mConfigs.getMaxFailedJobsInARowBeforeConnectionDisable()).thenReturn(MAX_FAILURE_JOBS_IN_A_ROW);

      autoDisableActivity.autoDisableFailingConnection(ACTIVITY_INPUT);
      Assertions.assertThat(standardSync.getStatus()).isEqualTo(Status.ACTIVE);
    }

    @Test
    @DisplayName("Test that the connection is _not_ disabled after 0 jobs in last MAX_DAYS_OF_STRAIGHT_FAILURE days")
    public void testNoRuns() throws IOException {
      Mockito.when(mJobPersistence.listJobStatusWithConnection(CONNECTION_ID, ConfigType.SYNC,
          CURR_INSTANT.minus(mConfigs.getMaxDaysOfOnlyFailedJobsBeforeConnectionDisable(), ChronoUnit.DAYS))).thenReturn(Collections.emptyList());

      autoDisableActivity.autoDisableFailingConnection(ACTIVITY_INPUT);
      Assertions.assertThat(standardSync.getStatus()).isEqualTo(Status.ACTIVE);
    }

    @Test
    @DisplayName("Test that the connection is disabled after only failed jobs in last MAX_DAYS_OF_STRAIGHT_FAILURE days")
    public void testOnlyFailuresInMaxDays() throws IOException, JsonValidationException, ConfigNotFoundException {
      Mockito.when(mJobPersistence.listJobStatusWithConnection(CONNECTION_ID, ConfigType.SYNC,
          CURR_INSTANT.minus(mConfigs.getMaxDaysOfOnlyFailedJobsBeforeConnectionDisable(), ChronoUnit.DAYS)))
          .thenReturn(Collections.singletonList(JobStatus.FAILED));
      Mockito.when(mConfigRepository.getStandardSync(CONNECTION_ID)).thenReturn(standardSync);
      Mockito.when(mConfigs.getMaxFailedJobsInARowBeforeConnectionDisable()).thenReturn(MAX_FAILURE_JOBS_IN_A_ROW);

      autoDisableActivity.autoDisableFailingConnection(ACTIVITY_INPUT);
      Assertions.assertThat(standardSync.getStatus()).isEqualTo(Status.INACTIVE);
    }

  }

}
