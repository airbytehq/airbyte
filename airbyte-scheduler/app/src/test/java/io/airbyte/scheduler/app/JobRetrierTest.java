/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.app;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoMoreInteractions;
import static org.mockito.Mockito.when;

import io.airbyte.config.JobConfig;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import io.airbyte.scheduler.persistence.JobNotifier;
import io.airbyte.scheduler.persistence.JobPersistence;
import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class JobRetrierTest {

  private static final Instant NOW = Instant.now();

  private JobNotifier jobNotifier;
  private JobPersistence persistence;
  private JobRetrier jobRetrier;
  private Job incompleteSyncJob;
  private Job incompleteSpecJob;

  @BeforeEach
  void setup() throws IOException {
    jobNotifier = mock(JobNotifier.class);
    persistence = mock(JobPersistence.class);

    jobRetrier = new JobRetrier(persistence, () -> NOW, jobNotifier);
    incompleteSyncJob = mock(Job.class);
    when(incompleteSyncJob.getId()).thenReturn(12L);
    when(incompleteSyncJob.getStatus()).thenReturn(JobStatus.INCOMPLETE);
    when(incompleteSyncJob.getConfigType()).thenReturn(JobConfig.ConfigType.SYNC);

    incompleteSpecJob = mock(Job.class);
    when(incompleteSpecJob.getId()).thenReturn(42L);
    when(incompleteSpecJob.getStatus()).thenReturn(JobStatus.INCOMPLETE);
    when(incompleteSpecJob.getConfigType()).thenReturn(JobConfig.ConfigType.GET_SPEC);
  }

  @Test
  void testSyncJobTimeToRetry() throws IOException {
    when(persistence.listJobsWithStatus(JobStatus.INCOMPLETE)).thenReturn(List.of(incompleteSyncJob));
    when(incompleteSyncJob.getAttemptsCount()).thenReturn(1);
    when(incompleteSyncJob.getUpdatedAtInSecond()).thenReturn(NOW.minus(Duration.ofMinutes(2)).getEpochSecond());

    jobRetrier.run();

    verify(persistence).listJobsWithStatus(JobStatus.INCOMPLETE);
    verify(persistence).resetJob(incompleteSyncJob.getId());
    verifyNoMoreInteractions(persistence);
  }

  @Test
  void testToSoonToRetry() throws IOException {
    when(persistence.listJobsWithStatus(JobStatus.INCOMPLETE)).thenReturn(List.of(incompleteSyncJob));
    when(incompleteSyncJob.getAttemptsCount()).thenReturn(1);
    when(incompleteSyncJob.getUpdatedAtInSecond()).thenReturn(NOW.minus(Duration.ofSeconds(10)).getEpochSecond());

    jobRetrier.run();

    verify(persistence).listJobsWithStatus(JobStatus.INCOMPLETE);
    verifyNoMoreInteractions(persistence);
  }

  @Test
  void testTooManySyncJobFailures() throws IOException {
    when(persistence.listJobsWithStatus(JobStatus.INCOMPLETE)).thenReturn(List.of(incompleteSyncJob));
    when(incompleteSyncJob.getAttemptsCount()).thenReturn(5);
    when(incompleteSyncJob.getUpdatedAtInSecond()).thenReturn(NOW.minus(Duration.ofMinutes(2)).getEpochSecond());

    jobRetrier.run();

    verify(persistence).listJobsWithStatus(JobStatus.INCOMPLETE);
    verify(persistence).failJob(incompleteSyncJob.getId());
    verifyNoMoreInteractions(persistence);
  }

  @Test
  void testSpecJobFailure() throws IOException {
    when(persistence.listJobsWithStatus(JobStatus.INCOMPLETE)).thenReturn(List.of(incompleteSpecJob));
    when(incompleteSpecJob.getAttemptsCount()).thenReturn(1);

    jobRetrier.run();

    verify(persistence).listJobsWithStatus(JobStatus.INCOMPLETE);
    verify(persistence).failJob(incompleteSpecJob.getId());
    verifyNoMoreInteractions(persistence);
  }

}
