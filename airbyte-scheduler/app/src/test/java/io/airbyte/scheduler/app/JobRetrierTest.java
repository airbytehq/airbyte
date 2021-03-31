/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.scheduler.app;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoMoreInteractions;
import static org.mockito.Mockito.when;

import io.airbyte.config.JobConfig;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import io.airbyte.scheduler.persistence.JobPersistence;
import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class JobRetrierTest {

  private static final Instant NOW = Instant.now();

  private JobPersistence persistence;
  private JobRetrier jobRetrier;
  private Job incompleteSyncJob;
  private Job incompleteSpecJob;

  @BeforeEach
  void setup() throws IOException {
    persistence = mock(JobPersistence.class);
    jobRetrier = new JobRetrier(persistence, () -> NOW);
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
