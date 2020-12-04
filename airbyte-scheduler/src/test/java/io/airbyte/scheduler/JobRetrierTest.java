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
import io.airbyte.scheduler.persistence.JobPersistence;
import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import java.util.Collections;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class JobRetrierTest {

  private static final Instant NOW = Instant.now();

  private JobPersistence persistence;
  private JobRetrier jobRetrier;
  private Job job;

  @BeforeEach
  void setup() throws IOException {
    persistence = mock(JobPersistence.class);
    jobRetrier = new JobRetrier(persistence, () -> NOW);
    job = mock(Job.class);
    when(job.getId()).thenReturn(12L);
    when(job.getStatus()).thenReturn(JobStatus.INCOMPLETE);

    when(persistence.listJobsWithStatus(JobConfig.ConfigType.SYNC, JobStatus.INCOMPLETE))
        .thenReturn(Collections.singletonList(job));
  }

  @Test
  void testTimeToRetry() throws IOException {
    when(job.getAttemptsCount()).thenReturn(1);
    when(job.getUpdatedAtInSecond()).thenReturn(NOW.minus(Duration.ofMinutes(2)).getEpochSecond());

    jobRetrier.run();

    verify(persistence).listJobsWithStatus(JobConfig.ConfigType.SYNC, JobStatus.INCOMPLETE);
    verify(persistence).resetJob(12L);
    verifyNoMoreInteractions(persistence);
  }

  @Test
  void testToSoonToRetry() throws IOException {
    when(job.getAttemptsCount()).thenReturn(1);
    when(job.getUpdatedAtInSecond()).thenReturn(NOW.minus(Duration.ofSeconds(10)).getEpochSecond());

    jobRetrier.run();

    verify(persistence).listJobsWithStatus(JobConfig.ConfigType.SYNC, JobStatus.INCOMPLETE);
    verifyNoMoreInteractions(persistence);
  }

  @Test
  void testTooManyFailures() throws IOException {
    when(job.getAttemptsCount()).thenReturn(5);
    when(job.getUpdatedAtInSecond()).thenReturn(NOW.minus(Duration.ofMinutes(2)).getEpochSecond());

    jobRetrier.run();

    verify(persistence).listJobsWithStatus(JobConfig.ConfigType.SYNC, JobStatus.INCOMPLETE);
    verify(persistence).failJob(12L);
    verifyNoMoreInteractions(persistence);
  }

}
