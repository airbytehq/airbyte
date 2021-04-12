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

package io.airbyte.scheduler.app.worker_run;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobResetConnectionConfig;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.scheduler.models.Job;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.temporal.TemporalClient;
import io.airbyte.workers.temporal.TemporalResponse;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

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

  @SuppressWarnings("unchecked")
  @Test
  void testSync() throws Exception {
    when(job.getConfigType()).thenReturn(ConfigType.SYNC);
    final TemporalResponse<StandardSyncOutput> mockResponse = mock(TemporalResponse.class);
    when(temporalClient.submitSync(JOB_ID, ATTEMPT_ID, job.getConfig().getSync())).thenReturn(mockResponse);

    final WorkerRun workerRun = workerRunFactory.create(job);
    workerRun.call();
    verify(temporalClient).submitSync(JOB_ID, ATTEMPT_ID, job.getConfig().getSync());
    assertEquals(jobRoot, workerRun.getJobRoot());
  }

  @SuppressWarnings("unchecked")
  @Test
  void testResetConnection() throws Exception {
    final JobResetConnectionConfig resetConfig = new JobResetConnectionConfig()
        .withDestinationDockerImage("airbyte/fusion_reactor")
        .withDestinationConfiguration(Jsons.jsonNode(ImmutableMap.of("a", 1)))
        .withConfiguredAirbyteCatalog(new ConfiguredAirbyteCatalog());
    final JobSyncConfig syncConfig = new JobSyncConfig()
        .withSourceDockerImage(WorkerConstants.RESET_JOB_SOURCE_DOCKER_IMAGE_STUB)
        .withDestinationDockerImage(resetConfig.getDestinationDockerImage())
        .withDestinationConfiguration(resetConfig.getDestinationConfiguration())
        .withSourceConfiguration(Jsons.emptyObject())
        .withConfiguredAirbyteCatalog(resetConfig.getConfiguredAirbyteCatalog());
    when(job.getConfigType()).thenReturn(ConfigType.RESET_CONNECTION);
    when(job.getConfig().getResetConnection()).thenReturn(resetConfig);
    final TemporalResponse<StandardSyncOutput> mockResponse = mock(TemporalResponse.class);
    when(temporalClient.submitSync(JOB_ID, ATTEMPT_ID, syncConfig)).thenReturn(mockResponse);

    final WorkerRun workerRun = workerRunFactory.create(job);
    workerRun.call();

    final ArgumentCaptor<JobSyncConfig> argument = ArgumentCaptor.forClass(JobSyncConfig.class);
    verify(temporalClient).submitSync(eq(JOB_ID), eq(ATTEMPT_ID), argument.capture());
    assertEquals(syncConfig, argument.getValue());
    assertEquals(jobRoot, workerRun.getJobRoot());
  }

}
