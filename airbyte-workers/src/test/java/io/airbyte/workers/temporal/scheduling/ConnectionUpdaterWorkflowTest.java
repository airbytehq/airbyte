/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import io.airbyte.config.JobConfig;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.temporal.scheduling.activities.GetSyncInputActivity;
import io.airbyte.workers.temporal.scheduling.activities.GetSyncInputActivityImpl;
import io.airbyte.workers.temporal.sync.EmptySyncWorkflow;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.testing.TestWorkflowEnvironment;
import io.temporal.worker.Worker;
import java.time.Duration;
import java.util.UUID;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

public class ConnectionUpdaterWorkflowTest {

  private static final String TASK_QUEUE = "queue";

  private TestWorkflowEnvironment testEnv;
  private Worker worker;
  private WorkflowClient client;

  private ConnectionUpdaterWorkflow connectionUpdaterWorkflow;

  private GetSyncInputActivityImpl getSyncInputActivity;

  @BeforeEach
  public void setUp() {
    testEnv = TestWorkflowEnvironment.newInstance();

    worker = testEnv.newWorker(TASK_QUEUE);
    worker.registerWorkflowImplementationTypes(ConnectionUpdaterWorkflowImpl.class);
    worker.registerWorkflowImplementationTypes(EmptySyncWorkflow.class);

    getSyncInputActivity = Mockito.mock(GetSyncInputActivityImpl.class);

    client = testEnv.getWorkflowClient();

  }

  private void execute(final ConnectionUpdaterInput input) {
    worker.registerActivitiesImplementations(getSyncInputActivity);
    testEnv.start();

    connectionUpdaterWorkflow = client.newWorkflowStub(
        ConnectionUpdaterWorkflow.class,
        WorkflowOptions.newBuilder().setTaskQueue(TASK_QUEUE).build());

    WorkflowClient.start(connectionUpdaterWorkflow::run, input);

    testEnv.sleep(Duration.ofDays(1));
  }

  @AfterEach
  public void tearDown() {
    testEnv.close();
  }

  @Test
  public void runSuccess() {
    final ConnectionUpdaterInput input = new ConnectionUpdaterInput(
        UUID.randomUUID(),
        1,
        new JobConfig(),
        1);

    Mockito.when(getSyncInputActivity.getSyncWorkflowInput(Mockito.any(GetSyncInputActivity.Input.class)))
        .thenReturn(
            new GetSyncInputActivity.Output(
                new JobRunConfig(),
                new IntegrationLauncherConfig(),
                new IntegrationLauncherConfig(),
                new StandardSyncInput()));

    execute(input);
  }

}
