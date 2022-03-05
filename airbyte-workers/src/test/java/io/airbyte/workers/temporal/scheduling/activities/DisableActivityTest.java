/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static io.airbyte.workers.temporal.scheduling.activities.DisableActivityImpl.MAX_DAYS_OF_STRAIGHT_FAILURE;
import static io.airbyte.workers.temporal.scheduling.activities.DisableActivityImpl.MAX_FAILURE_JOBS_IN_A_ROW;

import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.Status;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.temporal.scheduling.activities.DisableActivity.DisableActivityInput;
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
class DisableActivityTest {

  @Mock
  private ConfigRepository mConfigRepository;

  @Mock
  private JobPersistence mJobPersistence;

  @Mock
  private Job mJobFailure;

  @Mock
  private Job mJobSuccess;

  @InjectMocks
  private DisableActivityImpl disableActivity;

  private final static UUID connectionId = UUID.randomUUID();
  private final static StandardSync standardSync = new StandardSync();
  private static final Instant currInstant = Instant.now();
  private static final DisableActivityInput input = new DisableActivityInput(connectionId, currInstant);

  @BeforeEach
  void setUp() {
    standardSync.setStatus(Status.ACTIVE);
  }

  @Nested
  class DisableConnectionTest {

    @Test
    @DisplayName("Test that the connection is disabled after MAX_FAILURE_JOBS_IN_A_ROW straight failures")
    public void testMaxFailuresInARow() throws IOException, JsonValidationException, ConfigNotFoundException {
      // 1 success followed by MAX_FAILURE_JOBS_IN_A_ROW failures
      final List<Job> jobs = new ArrayList<>(Collections.singletonList(mJobSuccess));
      jobs.addAll(Collections.nCopies(MAX_FAILURE_JOBS_IN_A_ROW, mJobFailure));

      Mockito.when(mJobPersistence.listJobs(ConfigType.SYNC, currInstant.minus(MAX_DAYS_OF_STRAIGHT_FAILURE, ChronoUnit.DAYS)))
          .thenReturn(jobs);
      Mockito.when(mJobFailure.getStatus()).thenReturn(JobStatus.FAILED);
      Mockito.when(mConfigRepository.getStandardSync(connectionId))
          .thenReturn(standardSync);

      disableActivity.disableConnection(input);
      Assertions.assertThat(standardSync.getStatus()).isEqualTo(Status.INACTIVE);
    }

    @Test
    @DisplayName("Test that the connection is _not_ disabled after MAX_FAILURE_JOBS_IN_A_ROW - 1 straight failures")
    public void testLessThanMaxFailuresInARow() throws IOException {
      // 1 success followed by MAX_FAILURE_JOBS_IN_A_ROW-1 failures
      final List<Job> jobs = new ArrayList<>(Collections.singletonList(mJobSuccess));
      jobs.addAll(Collections.nCopies(MAX_FAILURE_JOBS_IN_A_ROW - 1, mJobFailure));

      Mockito.when(mJobPersistence.listJobs(ConfigType.SYNC, currInstant.minus(MAX_DAYS_OF_STRAIGHT_FAILURE, ChronoUnit.DAYS)))
          .thenReturn(jobs);
      Mockito.when(mJobFailure.getStatus()).thenReturn(JobStatus.FAILED);
      Mockito.when(mJobSuccess.getStatus()).thenReturn(JobStatus.SUCCEEDED);

      disableActivity.disableConnection(input);
      Assertions.assertThat(standardSync.getStatus()).isEqualTo(Status.ACTIVE);
    }

    @Test
    @DisplayName("Test that the connection is _not_ disabled after 0 jobs in last MAX_DAYS_OF_STRAIGHT_FAILURE days")
    public void testNoRuns() throws IOException {
      Mockito.when(mJobPersistence.listJobs(ConfigType.SYNC, currInstant.minus(MAX_DAYS_OF_STRAIGHT_FAILURE, ChronoUnit.DAYS)))
          .thenReturn(Collections.emptyList());

      disableActivity.disableConnection(input);
      Assertions.assertThat(standardSync.getStatus()).isEqualTo(Status.ACTIVE);
    }

    @Test
    @DisplayName("Test that the connection is disabled after only failed jobs in last MAX_DAYS_OF_STRAIGHT_FAILURE days")
    public void testOnlyFailuresInMaxDays() throws IOException, JsonValidationException, ConfigNotFoundException {
      Mockito.when(mJobPersistence.listJobs(ConfigType.SYNC, currInstant.minus(MAX_DAYS_OF_STRAIGHT_FAILURE, ChronoUnit.DAYS)))
          .thenReturn(Collections.singletonList(mJobFailure));
      Mockito.when(mJobFailure.getStatus()).thenReturn(JobStatus.FAILED);
      Mockito.when(mConfigRepository.getStandardSync(connectionId))
          .thenReturn(standardSync);

      disableActivity.disableConnection(input);
      Assertions.assertThat(standardSync.getStatus()).isEqualTo(Status.INACTIVE);
    }

  }

}
