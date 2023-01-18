/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.run;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.temporal.TemporalClient;
import io.airbyte.commons.temporal.TemporalResponse;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobResetConnectionConfig;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.persistence.job.models.Job;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.workers.WorkerConstants;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

class TemporalWorkerRunFactoryTest {

  private static final UUID CONNECTION_ID = UUID.randomUUID();
  private static final long JOB_ID = 10L;
  private static final int ATTEMPT_ID = 20;

  private Path jobRoot;
  private TemporalClient temporalClient;
  private TemporalWorkerRunFactory workerRunFactory;
  private Job job;

  @BeforeEach
  void setup() throws IOException {
    final Path workspaceRoot = Files.createTempDirectory(Path.of("/tmp"), "temporal_worker_run_test");
    jobRoot = workspaceRoot.resolve(String.valueOf(JOB_ID)).resolve(String.valueOf(ATTEMPT_ID));
    temporalClient = mock(TemporalClient.class);
    workerRunFactory = new TemporalWorkerRunFactory(
        temporalClient,
        workspaceRoot,
        "unknown airbyte version",
        mock(FeatureFlags.class));
    job = mock(Job.class, RETURNS_DEEP_STUBS);
    when(job.getId()).thenReturn(JOB_ID);
    when(job.getAttemptsCount()).thenReturn(ATTEMPT_ID);
    when(job.getScope()).thenReturn(CONNECTION_ID.toString());
  }

  @SuppressWarnings("unchecked")
  @Test
  void testSync() throws Exception {
    when(job.getConfigType()).thenReturn(ConfigType.SYNC);
    final TemporalResponse<StandardSyncOutput> mockResponse = mock(TemporalResponse.class);
    when(temporalClient.submitSync(JOB_ID, ATTEMPT_ID, job.getConfig().getSync(),
        CONNECTION_ID)).thenReturn(mockResponse);
    final WorkerRun workerRun = workerRunFactory.create(job);
    workerRun.call();
    verify(temporalClient).submitSync(JOB_ID, ATTEMPT_ID, job.getConfig().getSync(), CONNECTION_ID);
    assertEquals(jobRoot, workerRun.getJobRoot());
  }

  @SuppressWarnings("unchecked")
  @Test
  void testResetConnection() throws Exception {
    final JobResetConnectionConfig resetConfig = new JobResetConnectionConfig()
        .withDestinationDockerImage("airbyte/fusion_reactor")
        .withDestinationConfiguration(Jsons.jsonNode(ImmutableMap.of("a", 1)))
        .withOperationSequence(List.of(new StandardSyncOperation().withName("b")))
        .withConfiguredAirbyteCatalog(new ConfiguredAirbyteCatalog())
        .withIsSourceCustomConnector(false)
        .withIsDestinationCustomConnector(false);
    final JobSyncConfig syncConfig = new JobSyncConfig()
        .withSourceDockerImage(WorkerConstants.RESET_JOB_SOURCE_DOCKER_IMAGE_STUB)
        .withDestinationDockerImage(resetConfig.getDestinationDockerImage())
        .withDestinationConfiguration(resetConfig.getDestinationConfiguration())
        .withOperationSequence(List.of(new StandardSyncOperation().withName("b")))
        .withSourceConfiguration(Jsons.emptyObject())
        .withConfiguredAirbyteCatalog(resetConfig.getConfiguredAirbyteCatalog())
        .withIsSourceCustomConnector(false)
        .withIsDestinationCustomConnector(false);
    when(job.getConfigType()).thenReturn(ConfigType.RESET_CONNECTION);
    when(job.getConfig().getResetConnection()).thenReturn(resetConfig);
    final TemporalResponse<StandardSyncOutput> mockResponse = mock(TemporalResponse.class);
    when(temporalClient.submitSync(JOB_ID, ATTEMPT_ID, syncConfig, CONNECTION_ID)).thenReturn(mockResponse);

    final WorkerRun workerRun = workerRunFactory.create(job);
    workerRun.call();

    final ArgumentCaptor<JobSyncConfig> argument = ArgumentCaptor.forClass(JobSyncConfig.class);
    verify(temporalClient).submitSync(eq(JOB_ID), eq(ATTEMPT_ID), argument.capture(), eq(CONNECTION_ID));
    assertEquals(syncConfig, argument.getValue());
    assertEquals(jobRoot, workerRun.getJobRoot());
  }

}
