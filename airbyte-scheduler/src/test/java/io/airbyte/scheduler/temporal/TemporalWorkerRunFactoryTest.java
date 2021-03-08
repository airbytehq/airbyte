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

package io.airbyte.scheduler.temporal;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.worker_run.WorkerRun;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.EnumSource;

class TemporalWorkerRunFactoryTest {

  private static final long JOB_ID = 10L;
  private static final int ATTEMPT_ID = 20;

  private Path jobRoot;
  private TemporalClient temporalClient;
  private TemporalWorkerRunFactory workerRunFactory;
  private Job job;

  @BeforeEach
  void setup() throws IOException {
    Path workspaceRoot = Files.createTempDirectory(Path.of("/tmp"), "temporal_worker_run_test");
    jobRoot = workspaceRoot.resolve(String.valueOf(JOB_ID)).resolve(String.valueOf(ATTEMPT_ID));
    temporalClient = mock(TemporalClient.class);
    workerRunFactory = new TemporalWorkerRunFactory(temporalClient, workspaceRoot);
    job = mock(Job.class, RETURNS_DEEP_STUBS);
    when(job.getId()).thenReturn(JOB_ID);
    when(job.getAttemptsCount()).thenReturn(ATTEMPT_ID);
  }

  @Test
  void testGetSpec() throws Exception {
    when(job.getConfigType()).thenReturn(ConfigType.GET_SPEC);
    final WorkerRun workerRun = workerRunFactory.create(job);
    workerRun.call();
    verify(temporalClient).submitGetSpec(JOB_ID, ATTEMPT_ID, job.getConfig().getGetSpec());
    assertEquals(jobRoot, workerRun.getJobRoot());
  }

  @ParameterizedTest
  @EnumSource(value = ConfigType.class,
              names = {"CHECK_CONNECTION_SOURCE", "CHECK_CONNECTION_DESTINATION"})
  void testCheckConnection(ConfigType value) throws Exception {
    when(job.getConfigType()).thenReturn(value);
    final WorkerRun workerRun = workerRunFactory.create(job);
    workerRun.call();
    verify(temporalClient).submitCheckConnection(JOB_ID, ATTEMPT_ID, job.getConfig().getCheckConnection());
    assertEquals(jobRoot, workerRun.getJobRoot());
  }

  @Test
  void testDiscoverCatalog() throws Exception {
    when(job.getConfigType()).thenReturn(ConfigType.DISCOVER_SCHEMA);
    final WorkerRun workerRun = workerRunFactory.create(job);
    workerRun.call();
    verify(temporalClient).submitDiscoverSchema(JOB_ID, ATTEMPT_ID, job.getConfig().getDiscoverCatalog());
    assertEquals(jobRoot, workerRun.getJobRoot());
  }

  @Test
  void testSync() throws Exception {
    when(job.getConfigType()).thenReturn(ConfigType.SYNC);
    final WorkerRun workerRun = workerRunFactory.create(job);
    workerRun.call();
    verify(temporalClient).submitSync(JOB_ID, ATTEMPT_ID, job.getConfig().getSync());
    assertEquals(jobRoot, workerRun.getJobRoot());
  }

}
