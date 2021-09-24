/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.scheduler.models.Job;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.temporal.TemporalClient;
import io.airbyte.workers.temporal.TemporalResponse;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
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
        .withOperationSequence(List.of(new StandardSyncOperation().withName("b")))
        .withConfiguredAirbyteCatalog(new ConfiguredAirbyteCatalog());
    final JobSyncConfig syncConfig = new JobSyncConfig()
        .withSourceDockerImage(WorkerConstants.RESET_JOB_SOURCE_DOCKER_IMAGE_STUB)
        .withDestinationDockerImage(resetConfig.getDestinationDockerImage())
        .withDestinationConfiguration(resetConfig.getDestinationConfiguration())
        .withOperationSequence(List.of(new StandardSyncOperation().withName("b")))
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
