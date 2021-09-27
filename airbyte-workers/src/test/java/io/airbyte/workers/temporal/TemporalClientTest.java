/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobDiscoverCatalogConfig;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.temporal.client.WorkflowClient;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

class TemporalClientTest {

  private static final UUID JOB_UUID = UUID.randomUUID();
  private static final long JOB_ID = 11L;
  private static final int ATTEMPT_ID = 21;
  private static final JobRunConfig JOB_RUN_CONFIG = new JobRunConfig()
      .withJobId(String.valueOf(JOB_ID))
      .withAttemptId((long) ATTEMPT_ID);
  private static final String IMAGE_NAME1 = "hms invincible";
  private static final String IMAGE_NAME2 = "hms defiant";
  private static final IntegrationLauncherConfig UUID_LAUNCHER_CONFIG = new IntegrationLauncherConfig()
      .withJobId(String.valueOf(JOB_UUID))
      .withAttemptId((long) ATTEMPT_ID)
      .withDockerImage(IMAGE_NAME1);
  private static final IntegrationLauncherConfig LAUNCHER_CONFIG = new IntegrationLauncherConfig()
      .withJobId(String.valueOf(JOB_ID))
      .withAttemptId((long) ATTEMPT_ID)
      .withDockerImage(IMAGE_NAME1);

  private WorkflowClient workflowClient;
  private TemporalClient temporalClient;
  private Path logPath;

  @BeforeEach
  void setup() throws IOException {
    final Path workspaceRoot = Files.createTempDirectory(Path.of("/tmp"), "temporal_client_test");
    logPath = workspaceRoot.resolve(String.valueOf(JOB_ID)).resolve(String.valueOf(ATTEMPT_ID)).resolve(LogClientSingleton.LOG_FILENAME);
    workflowClient = mock(WorkflowClient.class);
    temporalClient = new TemporalClient(workflowClient, workspaceRoot);
  }

  @Nested
  @DisplayName("Test execute method.")
  class ExecuteJob {

    @SuppressWarnings("unchecked")
    @Test
    void testExecute() {
      final Supplier<String> supplier = mock(Supplier.class);
      when(supplier.get()).thenReturn("hello");

      final TemporalResponse<String> response = temporalClient.execute(JOB_RUN_CONFIG, supplier);

      assertNotNull(response);
      assertTrue(response.getOutput().isPresent());
      assertEquals("hello", response.getOutput().get());
      assertTrue(response.getMetadata().isSucceeded());
      assertEquals(logPath, response.getMetadata().getLogPath());
    }

    @SuppressWarnings("unchecked")
    @Test
    void testExecuteWithException() {
      final Supplier<String> supplier = mock(Supplier.class);
      when(supplier.get()).thenThrow(IllegalStateException.class);

      final TemporalResponse<String> response = temporalClient.execute(JOB_RUN_CONFIG, supplier);

      assertNotNull(response);
      assertFalse(response.getOutput().isPresent());
      assertFalse(response.getMetadata().isSucceeded());
      assertEquals(logPath, response.getMetadata().getLogPath());
    }

  }

  @Nested
  @DisplayName("Test job creation for each configuration type.")
  class TestJobSubmission {

    @Test
    void testSubmitGetSpec() {
      final SpecWorkflow specWorkflow = mock(SpecWorkflow.class);
      when(workflowClient.newWorkflowStub(SpecWorkflow.class, TemporalUtils.getWorkflowOptions(TemporalJobType.GET_SPEC))).thenReturn(specWorkflow);
      final JobGetSpecConfig getSpecConfig = new JobGetSpecConfig().withDockerImage(IMAGE_NAME1);

      temporalClient.submitGetSpec(JOB_UUID, ATTEMPT_ID, getSpecConfig);
      specWorkflow.run(JOB_RUN_CONFIG, UUID_LAUNCHER_CONFIG);
      verify(workflowClient).newWorkflowStub(SpecWorkflow.class, TemporalUtils.getWorkflowOptions(TemporalJobType.GET_SPEC));
    }

    @Test
    void testSubmitCheckConnection() {
      final CheckConnectionWorkflow checkConnectionWorkflow = mock(CheckConnectionWorkflow.class);
      when(workflowClient.newWorkflowStub(CheckConnectionWorkflow.class, TemporalUtils.getWorkflowOptions(TemporalJobType.CHECK_CONNECTION)))
          .thenReturn(checkConnectionWorkflow);
      final JobCheckConnectionConfig checkConnectionConfig = new JobCheckConnectionConfig()
          .withDockerImage(IMAGE_NAME1)
          .withConnectionConfiguration(Jsons.emptyObject());
      final StandardCheckConnectionInput input = new StandardCheckConnectionInput()
          .withConnectionConfiguration(checkConnectionConfig.getConnectionConfiguration());

      temporalClient.submitCheckConnection(JOB_UUID, ATTEMPT_ID, checkConnectionConfig);
      checkConnectionWorkflow.run(JOB_RUN_CONFIG, UUID_LAUNCHER_CONFIG, input);
      verify(workflowClient).newWorkflowStub(CheckConnectionWorkflow.class, TemporalUtils.getWorkflowOptions(TemporalJobType.CHECK_CONNECTION));
    }

    @Test
    void testSubmitDiscoverSchema() {
      final DiscoverCatalogWorkflow discoverCatalogWorkflow = mock(DiscoverCatalogWorkflow.class);
      when(workflowClient.newWorkflowStub(DiscoverCatalogWorkflow.class, TemporalUtils.getWorkflowOptions(TemporalJobType.DISCOVER_SCHEMA)))
          .thenReturn(discoverCatalogWorkflow);
      final JobDiscoverCatalogConfig checkConnectionConfig = new JobDiscoverCatalogConfig()
          .withDockerImage(IMAGE_NAME1)
          .withConnectionConfiguration(Jsons.emptyObject());
      final StandardDiscoverCatalogInput input = new StandardDiscoverCatalogInput()
          .withConnectionConfiguration(checkConnectionConfig.getConnectionConfiguration());

      temporalClient.submitDiscoverSchema(JOB_UUID, ATTEMPT_ID, checkConnectionConfig);
      discoverCatalogWorkflow.run(JOB_RUN_CONFIG, UUID_LAUNCHER_CONFIG, input);
      verify(workflowClient).newWorkflowStub(DiscoverCatalogWorkflow.class, TemporalUtils.getWorkflowOptions(TemporalJobType.DISCOVER_SCHEMA));
    }

    @Test
    void testSubmitSync() {
      final SyncWorkflow discoverCatalogWorkflow = mock(SyncWorkflow.class);
      when(workflowClient.newWorkflowStub(SyncWorkflow.class, TemporalUtils.getWorkflowOptions(TemporalJobType.SYNC)))
          .thenReturn(discoverCatalogWorkflow);
      final JobSyncConfig syncConfig = new JobSyncConfig()
          .withSourceDockerImage(IMAGE_NAME1)
          .withSourceDockerImage(IMAGE_NAME2)
          .withSourceConfiguration(Jsons.emptyObject())
          .withDestinationConfiguration(Jsons.emptyObject())
          .withOperationSequence(List.of())
          .withConfiguredAirbyteCatalog(new ConfiguredAirbyteCatalog());
      final StandardSyncInput input = new StandardSyncInput()
          .withNamespaceDefinition(syncConfig.getNamespaceDefinition())
          .withNamespaceFormat(syncConfig.getNamespaceFormat())
          .withPrefix(syncConfig.getPrefix())
          .withSourceConfiguration(syncConfig.getSourceConfiguration())
          .withDestinationConfiguration(syncConfig.getDestinationConfiguration())
          .withOperationSequence(syncConfig.getOperationSequence())
          .withCatalog(syncConfig.getConfiguredAirbyteCatalog())
          .withState(syncConfig.getState());

      final IntegrationLauncherConfig destinationLauncherConfig = new IntegrationLauncherConfig()
          .withJobId(String.valueOf(JOB_ID))
          .withAttemptId((long) ATTEMPT_ID)
          .withDockerImage(IMAGE_NAME2);

      temporalClient.submitSync(JOB_ID, ATTEMPT_ID, syncConfig);
      discoverCatalogWorkflow.run(JOB_RUN_CONFIG, LAUNCHER_CONFIG, destinationLauncherConfig, input);
      verify(workflowClient).newWorkflowStub(SyncWorkflow.class, TemporalUtils.getWorkflowOptions(TemporalJobType.SYNC));
    }

  }

}
