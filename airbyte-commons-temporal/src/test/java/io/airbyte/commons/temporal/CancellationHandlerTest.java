/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal;

import io.airbyte.commons.temporal.stubs.HeartbeatWorkflow;
import io.temporal.activity.Activity;
import io.temporal.activity.ActivityExecutionContext;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.testing.TestWorkflowEnvironment;
import io.temporal.worker.Worker;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class CancellationHandlerTest {

  @Test
  void testCancellationHandler() {

    final TestWorkflowEnvironment testEnv = TestWorkflowEnvironment.newInstance();

    final Worker worker = testEnv.newWorker("task-queue");

    worker.registerWorkflowImplementationTypes(HeartbeatWorkflow.HeartbeatWorkflowImpl.class);
    final WorkflowClient client = testEnv.getWorkflowClient();

    worker.registerActivitiesImplementations(new HeartbeatWorkflow.HeartbeatActivityImpl(() -> {
      final ActivityExecutionContext context = Activity.getExecutionContext();
      new CancellationHandler.TemporalCancellationHandler(context).checkAndHandleCancellation(() -> {});
    }));

    testEnv.start();

    final HeartbeatWorkflow heartbeatWorkflow = client.newWorkflowStub(
        HeartbeatWorkflow.class,
        WorkflowOptions.newBuilder()
            .setTaskQueue("task-queue")
            .build());

    Assertions.assertDoesNotThrow(heartbeatWorkflow::execute);

  }

}
