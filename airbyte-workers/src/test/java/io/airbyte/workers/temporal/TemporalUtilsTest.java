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

package io.airbyte.workers.temporal;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.doAnswer;
import static org.mockito.Mockito.mock;

import io.airbyte.commons.concurrency.VoidCallable;
import io.temporal.activity.ActivityCancellationType;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import io.temporal.activity.ActivityOptions;
import io.temporal.api.common.v1.WorkflowExecution;
import io.temporal.api.workflow.v1.WorkflowExecutionInfo;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.testing.TestWorkflowEnvironment;
import io.temporal.worker.Worker;
import io.temporal.workflow.Workflow;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;
import java.time.Duration;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TemporalUtilsTest {

  private static final String TASK_QUEUE = "default";

  @Test
  void testAsyncExecute() throws Exception {
    final CountDownLatch countDownLatch = new CountDownLatch(1);

    final VoidCallable callable = mock(VoidCallable.class);

    // force it to wait until we can verify that it is running.
    doAnswer((a) -> {
      countDownLatch.await(1, TimeUnit.MINUTES);
      return null;
    }).when(callable).call();

    final TestWorkflowEnvironment testEnv = TestWorkflowEnvironment.newInstance();
    final WorkflowServiceStubs temporalService = testEnv.getWorkflowService();
    final Worker worker = testEnv.newWorker(TASK_QUEUE);
    worker.registerWorkflowImplementationTypes(TestWorkflow.WorkflowImpl.class);
    final WorkflowClient client = testEnv.getWorkflowClient();
    worker.registerActivitiesImplementations(new TestWorkflow.Activity1Impl(callable));
    testEnv.start();

    final TestWorkflow workflowStub = client.newWorkflowStub(TestWorkflow.class, WorkflowOptions.newBuilder().setTaskQueue(TASK_QUEUE).build());
    final ImmutablePair<WorkflowExecution, CompletableFuture<String>> pair = TemporalUtils.asyncExecute(
        workflowStub,
        workflowStub::run,
        "whatever",
        String.class);

    final WorkflowExecution workflowExecution = pair.getLeft();
    final String workflowId = workflowExecution.getWorkflowId();
    final String runId = workflowExecution.getRunId();

    final WorkflowExecutionInfo workflowExecutionInfo = temporalService.blockingStub().listOpenWorkflowExecutions(null).getExecutionsList().get(0);
    assertEquals(workflowId, workflowExecutionInfo.getExecution().getWorkflowId());
    assertEquals(runId, workflowExecutionInfo.getExecution().getRunId());

    // allow the workflow to complete.
    countDownLatch.countDown();

    final String result = pair.getRight().get(1, TimeUnit.MINUTES);
    assertEquals("completed", result);
  }

  @WorkflowInterface
  public interface TestWorkflow {

    @WorkflowMethod
    String run(String arg);

    class WorkflowImpl implements TestWorkflow {

      private static final Logger LOGGER = LoggerFactory.getLogger(WorkflowImpl.class);

      private final ActivityOptions options = ActivityOptions.newBuilder()
          .setScheduleToCloseTimeout(Duration.ofDays(3))
          .setCancellationType(ActivityCancellationType.WAIT_CANCELLATION_COMPLETED)
          .setRetryOptions(TemporalUtils.NO_RETRY)
          .build();

      private final Activity1 activity1 = Workflow.newActivityStub(Activity1.class, options);
      private final Activity1 activity2 = Workflow.newActivityStub(Activity1.class, options);

      @Override
      public String run(String arg) {
        LOGGER.info("workflow before activity 1");
        activity1.activity();
        LOGGER.info("workflow before activity 2");
        activity2.activity();
        LOGGER.info("workflow after all activities");

        return "completed";
      }

    }

    @ActivityInterface
    interface Activity1 {

      @ActivityMethod
      void activity();

    }

    class Activity1Impl implements Activity1 {

      private static final Logger LOGGER = LoggerFactory.getLogger(TestWorkflow.Activity1Impl.class);
      private static final String ACTIVITY1 = "activity1";

      private final VoidCallable callable;

      public Activity1Impl(VoidCallable callable) {
        this.callable = callable;
      }

      public void activity() {
        LOGGER.info("before: {}", ACTIVITY1);
        try {
          callable.call();
        } catch (Exception e) {
          throw new RuntimeException(e);
        }
        LOGGER.info("before: {}", ACTIVITY1);
      }

    }

  }

}
