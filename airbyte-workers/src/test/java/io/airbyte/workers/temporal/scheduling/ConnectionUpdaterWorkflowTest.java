/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import io.airbyte.config.StandardSyncInput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivity.SyncInput;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivity.SyncOutput;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivityImpl;
import io.airbyte.workers.temporal.sync.EmptySyncWorkflow;
import io.temporal.client.WorkflowClient;
import io.temporal.testing.TestWorkflowEnvironment;
import io.temporal.testing.TestWorkflowExtension;
import io.temporal.worker.Worker;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.RegisterExtension;
import org.mockito.Mockito;

public class ConnectionUpdaterWorkflowTest {

  private static final GenerateInputActivityImpl getSyncInputActivity = Mockito.mock(GenerateInputActivityImpl.class);

  @BeforeEach
  public void setUp() {
    Mockito.reset(getSyncInputActivity);
  }

  @RegisterExtension
  public static final TestWorkflowExtension testWorkflowExtension =
      TestWorkflowExtension.newBuilder()
          .setWorkflowTypes(ConnectionUpdaterWorkflowImpl.class, EmptySyncWorkflow.class)
          .setActivityImplementations(getSyncInputActivity)
          .build();

  @Test
  public void runSuccess(final TestWorkflowEnvironment testEnv, final Worker worker, final ConnectionUpdaterWorkflow workflow) {
    final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
        UUID.randomUUID(),
        1L,
        1,
        false,
        1);

    Mockito.when(getSyncInputActivity.getSyncWorkflowInput(Mockito.any(SyncInput.class)))
        .thenReturn(
            new SyncOutput(
                new JobRunConfig(),
                new IntegrationLauncherConfig(),
                new IntegrationLauncherConfig(),
                new StandardSyncInput()));

    WorkflowClient.start(workflow::run, input);
  }

}
