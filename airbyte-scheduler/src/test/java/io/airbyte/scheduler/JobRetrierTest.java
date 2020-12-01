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

package io.airbyte.scheduler;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoMoreInteractions;
import static org.mockito.Mockito.when;

import io.airbyte.config.JobConfig;
import io.airbyte.scheduler.persistence.SchedulerPersistence;
import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import java.util.Collections;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class JobRetrierTest {

  private static final Instant NOW = Instant.now();

  private SchedulerPersistence persistence;
  private JobRetrier jobRetrier;
  private Job job;

  @BeforeEach
  void setup() {
    persistence = mock(SchedulerPersistence.class);
    jobRetrier = new JobRetrier(persistence, () -> NOW);
    job = mock(Job.class);
    when(job.getId()).thenReturn(12L);
  }

  @Test
  void testTimeToRetry() throws IOException {
    when(job.getNumAttempts()).thenReturn(1);
    when(job.getStatus()).thenReturn(JobStatus.FAILED);
    when(job.getUpdatedAtInSecond()).thenReturn(NOW.minus(Duration.ofMinutes(2)).getEpochSecond());

    when(persistence.listJobsWithStatus(JobConfig.ConfigType.SYNC, JobStatus.FAILED))
        .thenReturn(Collections.singletonList(job));

    jobRetrier.run();

    verify(persistence).listJobsWithStatus(JobConfig.ConfigType.SYNC, JobStatus.FAILED);
    verify(persistence).updateStatus(12L, JobStatus.PENDING);
    verifyNoMoreInteractions(persistence);

  }

  @Test
  void testToSoonToRetry() throws IOException {
    when(job.getNumAttempts()).thenReturn(1);
    when(job.getStatus()).thenReturn(JobStatus.FAILED);
    when(job.getUpdatedAtInSecond()).thenReturn(NOW.minus(Duration.ofSeconds(10)).getEpochSecond());

    when(persistence.listJobsWithStatus(JobConfig.ConfigType.SYNC, JobStatus.FAILED))
        .thenReturn(Collections.singletonList(job));

    jobRetrier.run();

    verify(persistence).listJobsWithStatus(JobConfig.ConfigType.SYNC, JobStatus.FAILED);
    verifyNoMoreInteractions(persistence);
  }

  @Test
  void testTooManyFailures() throws IOException {
    when(job.getNumAttempts()).thenReturn(5);
    when(job.getStatus()).thenReturn(JobStatus.FAILED);
    when(job.getUpdatedAtInSecond()).thenReturn(NOW.minus(Duration.ofMinutes(2)).getEpochSecond());

    when(persistence.listJobsWithStatus(JobConfig.ConfigType.SYNC, JobStatus.FAILED))
        .thenReturn(Collections.singletonList(job));

    jobRetrier.run();

    verify(persistence).listJobsWithStatus(JobConfig.ConfigType.SYNC, JobStatus.FAILED);
    verify(persistence).updateStatus(12L, JobStatus.CANCELLED);
    verifyNoMoreInteractions(persistence);
  }

}
