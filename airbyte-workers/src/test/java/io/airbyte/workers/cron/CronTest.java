/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.cron;

import io.airbyte.workers.cron.BasicWorkflow.BasicWorkflowImpl;
import io.airbyte.workers.cron.BasicWorkflow.CountingActivityImpl;
import io.airbyte.workers.cron.CreateWorkflowWorkflow.CreateWorkflowActivityImpl;
import io.airbyte.workers.cron.CreateWorkflowWorkflow.CreateWorkflowWorkflowImpl;
import io.airbyte.workers.cron.DeleteWorkflowWorkflow.DeleteWorkflowWorkflowImpl;
import io.airbyte.workers.cron.ManualWorkflowWorkflow.ManualWorkflowWorkflowImpl;
import io.airbyte.workers.cron.UpdateWorkflowWorkflow.UpdateWorkflowWorkflowImpl;
import io.temporal.api.common.v1.WorkflowExecution;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.client.WorkflowStub;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.testing.TestWorkflowEnvironment;
import io.temporal.worker.Worker;
import java.io.IOException;
import java.time.Duration;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class explores what it would look like to schedule each sync as a temporal cron job.
 *
 * Instead of our actual SyncWorkflow it is just executing a CountingWorkflow.
 *
 * It then shows what it would look like to use temporal workflows to create, update, delete, and
 * schedule a manual run. It does NOT implement the equivalent of reset, though with the provided
 * building blocks it should be straight forward.
 *
 * todo (cgardens) - map out composite cases. e.g. for a scheduled sync, while manual run is going,
 * what happens when we delete the connection. this will require us to be more thoughtful about the
 * the rules around which workflow mutation operations can run at once on a given workflow.
 *
 * Note: the dev rel who respond to questions on temporal seems to recommend against this approach:
 * https://community.temporal.io/t/temporal-cron-questions/201
 */
public class CronTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(UpdateWorkflowWorkflow.class);

  private static final String WORKFLOW_ID = "123"; // this would be connection id.

  @Test
  void test() throws InterruptedException, IOException {
    // SETUP
    final Map<String, AtomicInteger> counter = new ConcurrentHashMap<>();
    final TestWorkflowEnvironment testEnv = TestWorkflowEnvironment.newInstance();

    final WorkflowClient client = testEnv.getWorkflowClient();

    final Worker workerWorker = testEnv.newWorker(BasicWorkflow.WORKFLOW_NAME);
    workerWorker.registerWorkflowImplementationTypes(BasicWorkflowImpl.class);
    workerWorker.registerActivitiesImplementations(new CountingActivityImpl(counter));

    final Worker creatorWorker = testEnv.newWorker(CreateWorkflowWorkflow.WORKFLOW_NAME);
    creatorWorker.registerWorkflowImplementationTypes(CreateWorkflowWorkflowImpl.class);
    creatorWorker.registerActivitiesImplementations(new CreateWorkflowActivityImpl(client));

    final Worker updaterWorker = testEnv.newWorker(UpdateWorkflowWorkflow.WORKFLOW_NAME);
    updaterWorker.registerWorkflowImplementationTypes(UpdateWorkflowWorkflowImpl.class);
    updaterWorker.registerActivitiesImplementations(new UpdateWorkflowWorkflow.UpdateWorkflowActivityImpl(client));

    final Worker manualWorker = testEnv.newWorker(ManualWorkflowWorkflow.WORKFLOW_NAME);
    manualWorker.registerWorkflowImplementationTypes(ManualWorkflowWorkflowImpl.class);

    final Worker deleteWorker = testEnv.newWorker(DeleteWorkflowWorkflow.WORKFLOW_NAME);
    deleteWorker.registerWorkflowImplementationTypes(DeleteWorkflowWorkflowImpl.class);
    deleteWorker.registerActivitiesImplementations(new DeleteWorkflowWorkflow.TerminateWorkflowActivityImpl(client));

    testEnv.start();

    // in practice, we would create a different stub with an id scoped to the correct workflow id
    // (connection id). for sake of testing, just doing it statically.
    final CreateWorkflowWorkflow createWorkflowStub =
        client.newWorkflowStub(CreateWorkflowWorkflow.class, WorkflowOptions.newBuilder()
            .setTaskQueue(CreateWorkflowWorkflow.WORKFLOW_NAME)
            .setWorkflowId(WORKFLOW_ID + "-" + CreateWorkflowWorkflow.WORKFLOW_NAME)
            .build());
    final UpdateWorkflowWorkflow updateWorkflowStub =
        client.newWorkflowStub(UpdateWorkflowWorkflow.class, WorkflowOptions.newBuilder()
            .setTaskQueue(UpdateWorkflowWorkflow.WORKFLOW_NAME)
            .setWorkflowId(WORKFLOW_ID + "-" + UpdateWorkflowWorkflow.WORKFLOW_NAME)
            .setWorkflowId(WORKFLOW_ID + "-" + UpdateWorkflowWorkflow.WORKFLOW_NAME)
            .build());
    final DeleteWorkflowWorkflow deleteWorkflowStub =
        client.newWorkflowStub(DeleteWorkflowWorkflow.class, WorkflowOptions.newBuilder()
            .setTaskQueue(DeleteWorkflowWorkflow.WORKFLOW_NAME)
            .setWorkflowId(WORKFLOW_ID + "-" + DeleteWorkflowWorkflow.WORKFLOW_NAME)
            .build());
    final ManualWorkflowWorkflow manualWorkflowStub =
        client.newWorkflowStub(ManualWorkflowWorkflow.class, WorkflowOptions.newBuilder()
            .setTaskQueue(ManualWorkflowWorkflow.WORKFLOW_NAME)
            .setWorkflowId(WORKFLOW_ID + "-" + ManualWorkflowWorkflow.WORKFLOW_NAME)
            .build());

    final WorkflowServiceStubs temporalService = client.getWorkflowServiceStubs();

    final WorkflowExecution workflowExecution = WorkflowExecution.newBuilder()
        .setWorkflowId(WORKFLOW_ID)
        .build();

    // TEST RUN

    // create initial workflow
    LOGGER.info("creating initial workflow: started");
    createWorkflowStub.createWorkflow(WORKFLOW_ID, WORKFLOW_ID, "*/2 * * * *", BasicWorkflow.WORKFLOW_NAME);
    LOGGER.info("creating initial workflow: done");

    // verify it is running, we expect the counter to be non-zero after the sleep.
    testEnv.sleep(Duration.ofSeconds(1000));
    logCount(counter, "0");

    // verify the schedule is set.
    TemporalUtils.logSchedule(temporalService, workflowExecution, 1);

    // verify more records are produced as more time passes.
    testEnv.sleep(Duration.ofSeconds(1000));
    logCount(counter, "1");

    // update the workflow to use a new schedule
    LOGGER.info("updating workflow schedule: started");
    updateWorkflowStub.updateWorkflow(WORKFLOW_ID, WORKFLOW_ID, "*/5 * * * *", BasicWorkflow.WORKFLOW_NAME);
    LOGGER.info("updating workflow schedule: done");

    // verify more records are being produced with the new schedule.
    testEnv.sleep(Duration.ofSeconds(1000));
    logCount(counter, "1.5");

    // verify the schedule is updated.
    TemporalUtils.logSchedule(temporalService, workflowExecution, 2);

    LOGGER.info("trigger manual sync: started");
    manualWorkflowStub.manual(WORKFLOW_ID, WORKFLOW_ID, BasicWorkflow.WORKFLOW_NAME);
    LOGGER.info("trigger manual sync: done");

    logCount(counter, "1.70");
    testEnv.sleep(Duration.ofSeconds(1000));
    logCount(counter, "1.75");

    // terminate the workflow
    LOGGER.info("terminating workflow: started");
    deleteWorkflowStub.delete(WORKFLOW_ID);
    LOGGER.info("terminating workflow: done");

    logCount(counter, "2");

    // verify that the counter does NOT keep increasing because the workflow has stopped.
    testEnv.sleep(Duration.ofSeconds(1000));
    logCount(counter, "3");

    testEnv.shutdown();
  }

  private static void logCount(final Map<String, AtomicInteger> counter, final String id) {
    LOGGER.info("counter status (checkpoint: {}) - {}", id, counter);
  }

}
