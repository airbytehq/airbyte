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

import io.airbyte.scheduler.models.JobRunConfig;
import io.temporal.api.common.v1.WorkflowExecution;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.client.WorkflowStub;
import io.temporal.common.RetryOptions;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.serviceclient.WorkflowServiceStubsOptions;
import io.temporal.workflow.Functions;
import java.io.Serializable;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import org.apache.commons.lang3.tuple.ImmutablePair;

public class TemporalUtils {

  public static WorkflowServiceStubs createTemporalService(String temporalHost) {
    final WorkflowServiceStubsOptions options = WorkflowServiceStubsOptions.newBuilder()
        // todo move to env.
        .setTarget(temporalHost)
        .build();

    return WorkflowServiceStubs.newInstance(options);
  }

  public static WorkflowClient createTemporalClient(String temporalHost) {
    final WorkflowServiceStubs temporalService = createTemporalService(temporalHost);
    return WorkflowClient.newInstance(temporalService);
  }

  public static final RetryOptions NO_RETRY = RetryOptions.newBuilder().setMaximumAttempts(1).build();

  public static final String DEFAULT_NAMESPACE = "default";

  @FunctionalInterface
  public interface TemporalJobCreator<T extends Serializable> {

    UUID create(WorkflowClient workflowClient, long jobId, int attempt, T config);

  }

  public static WorkflowOptions getWorkflowOptions(TemporalJobType jobType) {
    return WorkflowOptions.newBuilder()
        .setRetryOptions(NO_RETRY)
        .setTaskQueue(jobType.name())
        // todo (cgardens) we do not leverage Temporal retries.
        .setRetryOptions(RetryOptions.newBuilder().setMaximumAttempts(1).build())
        .build();
  }

  public static JobRunConfig createJobRunConfig(UUID jobId, int attemptId) {
    return createJobRunConfig(String.valueOf(jobId), attemptId);
  }

  public static JobRunConfig createJobRunConfig(long jobId, int attemptId) {
    return createJobRunConfig(String.valueOf(jobId), attemptId);
  }

  public static JobRunConfig createJobRunConfig(String jobId, int attemptId) {
    return new JobRunConfig()
        .withJobId(jobId)
        .withAttemptId((long) attemptId);
  }

  /**
   * Allows running a given temporal workflow stub asynchronously. This method only works for
   * workflows that take one argument. Because of the iface that Temporal supplies, in order to handle
   * other method signatures, if we need to support them, we will need to add another helper with that
   * number of args. For a reference on how Temporal recommends to do this see their docs:
   * https://docs.temporal.io/docs/java/workflows#asynchronous-start
   *
   * @param workflowStub - workflow stub to be executed
   * @param function - function on the workflow stub to be executed
   * @param arg1 - argument to be supplied to the workflow function
   * @param outputType - class of the output type of the workflow function
   * @param <STUB> - type of the workflow stub
   * @param <A1> - type of the argument of the workflow stub
   * @param <R> - type of the return of the workflow stub
   * @return pair of the workflow execution (contains metadata on the asynchronously running job) and
   *         future that can be used to await the result of the workflow stub's function
   */
  public static <STUB, A1, R> ImmutablePair<WorkflowExecution, CompletableFuture<R>> asyncExecute(STUB workflowStub,
                                                                                                  Functions.Func1<A1, R> function,
                                                                                                  A1 arg1,
                                                                                                  Class<R> outputType) {
    final WorkflowStub untyped = WorkflowStub.fromTyped(workflowStub);
    final WorkflowExecution workflowExecution = WorkflowClient.start(function, arg1);
    final CompletableFuture<R> resultAsync = untyped.getResultAsync(outputType);
    return ImmutablePair.of(workflowExecution, resultAsync);
  }

}
