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

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;

import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.testing.TestWorkflowEnvironment;
import io.temporal.worker.Worker;
import java.util.function.Consumer;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

// based of example in temporal samples:
// https://github.com/temporalio/samples-java/blob/master/src/test/java/io/temporal/samples/hello/HelloActivityTest.java
@Disabled
class TemporalWorkflowTest {

  private static final String TASK_QUEUE = "a";

  private TestWorkflowEnvironment testEnv;
  private Worker worker;
  private WorkflowClient client;

  @BeforeEach
  public void setUp() {
    testEnv = TestWorkflowEnvironment.newInstance();
    worker = testEnv.newWorker(TASK_QUEUE);
    worker.registerWorkflowImplementationTypes(TestWorkflow.WorkflowImpl.class);

    client = testEnv.getWorkflowClient();
  }

  @SuppressWarnings("unchecked")
  @Test
  void test() {
    final Consumer<String> activity1Consumer = mock(Consumer.class);
    final Consumer<String> activity2Consumer = mock(Consumer.class);

    doThrow(new IllegalArgumentException("don't argue!")).when(activity1Consumer).accept(any());

    worker.registerActivitiesImplementations(new TestWorkflow.Activity1Impl(activity1Consumer), new TestWorkflow.Activity2Impl(activity2Consumer));
    testEnv.start();

    final TestWorkflow workflow = client.newWorkflowStub(TestWorkflow.class, WorkflowOptions.newBuilder().setTaskQueue(TASK_QUEUE).build());
    workflow.run();
  }

  @AfterEach
  public void tearDown() {
    testEnv.close();
  }

}
