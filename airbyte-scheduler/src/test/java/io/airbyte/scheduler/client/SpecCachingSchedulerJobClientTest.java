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

package io.airbyte.scheduler.client;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.JobStatus;
import io.airbyte.scheduler.persistence.JobCreator;
import java.io.IOException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SpecCachingSchedulerJobClientTest {

  private static final long JOB_ID = 14L;
  private static final String DOCKER_IMAGE = "airbyte/space_cop";

  private Job job;
  private JobCreator jobCreator;
  private CachingSchedulerJobClient client;

  @BeforeEach
  void setup() throws IOException {
    job = mock(Job.class);
    jobCreator = mock(JobCreator.class);
    client = spy(new SpecCachingSchedulerJobClient(null, jobCreator));

    when(jobCreator.createGetSpecJob(DOCKER_IMAGE)).thenReturn(JOB_ID);
    doReturn(job).when((DefaultSchedulerJobClient) client).waitUntilJobIsTerminalOrTimeout(JOB_ID);
    when(job.getStatus()).thenReturn(JobStatus.SUCCEEDED);
  }

  @Test
  void testCreateGetSpecJobCacheCacheMiss() throws IOException {
    assertEquals(job, client.createGetSpecJob(DOCKER_IMAGE));
    verify(jobCreator, times(1)).createGetSpecJob(DOCKER_IMAGE);
  }

  @Test
  void testCreateGetSpecJobFails() throws IOException {
    when(job.getStatus()).thenReturn(JobStatus.FAILED);
    client.createGetSpecJob(DOCKER_IMAGE);
    assertEquals(job, client.createGetSpecJob(DOCKER_IMAGE));
    verify(jobCreator, times(2)).createGetSpecJob(DOCKER_IMAGE);
  }

  @Test
  void testCreateGetSpecJobCacheCacheHit() throws IOException {
    client.createGetSpecJob(DOCKER_IMAGE);
    assertEquals(job, client.createGetSpecJob(DOCKER_IMAGE));
    verify(jobCreator, times(1)).createGetSpecJob(DOCKER_IMAGE);
  }

  @Test
  void testInvalidateCache() throws IOException {
    client.createGetSpecJob(DOCKER_IMAGE);
    client.resetCache();
    assertEquals(job, client.createGetSpecJob(DOCKER_IMAGE));
    verify(jobCreator, times(2)).createGetSpecJob(DOCKER_IMAGE);
  }

}
