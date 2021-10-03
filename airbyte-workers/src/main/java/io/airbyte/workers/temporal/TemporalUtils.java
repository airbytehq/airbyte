/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal;

import static java.util.stream.Collectors.toSet;

import io.airbyte.commons.lang.Exceptions;
import io.airbyte.scheduler.models.JobRunConfig;
import io.temporal.api.common.v1.WorkflowExecution;
import io.temporal.api.namespace.v1.NamespaceInfo;
import io.temporal.api.workflowservice.v1.DescribeNamespaceResponse;
import io.temporal.api.workflowservice.v1.ListNamespacesRequest;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.client.WorkflowStub;
import io.temporal.common.RetryOptions;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.serviceclient.WorkflowServiceStubsOptions;
import io.temporal.workflow.Functions;
import java.io.Serializable;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TemporalUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(TemporalUtils.class);

  public static WorkflowServiceStubs createTemporalService(String temporalHost) {
    final WorkflowServiceStubsOptions options = WorkflowServiceStubsOptions.newBuilder()
        // todo move to env.
        .setTarget(temporalHost)
        .build();

    final WorkflowServiceStubs temporalService = WorkflowServiceStubs.newInstance(options);
    waitForTemporalServerAndLog(temporalService);
    return temporalService;
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

  public static void waitForTemporalServerAndLog(WorkflowServiceStubs temporalService) {
    LOGGER.info("Waiting for temporal server...");

    boolean temporalStatus = false;

    while (!temporalStatus) {
      LOGGER.warn("Waiting for default namespace to be initialized in temporal...");
      Exceptions.toRuntime(() -> Thread.sleep(2000));

      try {
        temporalStatus = getNamespaces(temporalService).contains("default");
      } catch (Exception e) {
        // Ignore the exception because this likely means that the Temporal service is still initializing.
        LOGGER.warn("Ignoring exception while trying to request Temporal namespaces:", e);
      }
    }

    // sometimes it takes a few additional seconds for workflow queue listening to be available
    Exceptions.toRuntime(() -> Thread.sleep(5000));

    LOGGER.info("Found temporal default namespace!");
  }

  protected static Set<String> getNamespaces(WorkflowServiceStubs temporalService) {
    return temporalService.blockingStub()
        .listNamespaces(ListNamespacesRequest.newBuilder().build())
        .getNamespacesList()
        .stream()
        .map(DescribeNamespaceResponse::getNamespaceInfo)
        .map(NamespaceInfo::getName)
        .collect(toSet());
  }

}
