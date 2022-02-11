/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal;

import static java.util.stream.Collectors.toSet;

import io.airbyte.commons.lang.Exceptions;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.scheduler.models.JobRunConfig;
import io.temporal.activity.Activity;
import io.temporal.api.common.v1.WorkflowExecution;
import io.temporal.api.namespace.v1.NamespaceConfig;
import io.temporal.api.namespace.v1.NamespaceInfo;
import io.temporal.api.workflowservice.v1.DescribeNamespaceRequest;
import io.temporal.api.workflowservice.v1.DescribeNamespaceResponse;
import io.temporal.api.workflowservice.v1.ListNamespacesRequest;
import io.temporal.api.workflowservice.v1.UpdateNamespaceRequest;
import io.temporal.client.ActivityCompletionException;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.client.WorkflowStub;
import io.temporal.common.RetryOptions;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.serviceclient.WorkflowServiceStubsOptions;
import io.temporal.workflow.Functions;
import java.io.Serializable;
import java.time.Duration;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;
import org.apache.commons.lang3.time.DurationFormatUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TemporalUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(TemporalUtils.class);

  public static final Duration SEND_HEARTBEAT_INTERVAL = Duration.ofSeconds(10);
  public static final Duration HEARTBEAT_TIMEOUT = Duration.ofSeconds(30);

  public static WorkflowServiceStubs createTemporalService(final String temporalHost) {
    final WorkflowServiceStubsOptions options = WorkflowServiceStubsOptions.newBuilder()
        .setTarget(temporalHost) // todo: move to EnvConfigs
        .build();

    return getTemporalClientWhenConnected(
        Duration.ofSeconds(2),
        Duration.ofMinutes(2),
        Duration.ofSeconds(5),
        () -> WorkflowServiceStubs.newInstance(options));
  }

  public static final RetryOptions NO_RETRY = RetryOptions.newBuilder().setMaximumAttempts(1).build();

  private static final Configs configs = new EnvConfigs();
  public static final RetryOptions RETRY = RetryOptions.newBuilder()
      .setMaximumAttempts(configs.getActivityNumberOfAttempt())
      .setInitialInterval(Duration.ofSeconds(configs.getDelayBetweenActivityAttempts()))
      .build();

  public static final String DEFAULT_NAMESPACE = "default";

  private static final Duration WORKFLOW_EXECUTION_TTL = Duration.ofDays(7);
  private static final String HUMAN_READABLE_WORKFLOW_EXECUTION_TTL =
      DurationFormatUtils.formatDurationWords(WORKFLOW_EXECUTION_TTL.toMillis(), true, true);

  public static void configureTemporalNamespace(WorkflowServiceStubs temporalService) {
    final var client = temporalService.blockingStub();
    final var describeNamespaceRequest = DescribeNamespaceRequest.newBuilder().setNamespace(DEFAULT_NAMESPACE).build();
    final var currentRetentionGrpcDuration = client.describeNamespace(describeNamespaceRequest).getConfig().getWorkflowExecutionRetentionTtl();
    final var currentRetention = Duration.ofSeconds(currentRetentionGrpcDuration.getSeconds());

    if (currentRetention.equals(WORKFLOW_EXECUTION_TTL)) {
      LOGGER.info("Workflow execution TTL already set for namespace " + DEFAULT_NAMESPACE + ". Remains unchanged as: "
          + HUMAN_READABLE_WORKFLOW_EXECUTION_TTL);
    } else {
      final var newGrpcDuration = com.google.protobuf.Duration.newBuilder().setSeconds(WORKFLOW_EXECUTION_TTL.getSeconds()).build();
      final var humanReadableCurrentRetention = DurationFormatUtils.formatDurationWords(currentRetention.toMillis(), true, true);
      final var namespaceConfig = NamespaceConfig.newBuilder().setWorkflowExecutionRetentionTtl(newGrpcDuration).build();
      final var updateNamespaceRequest = UpdateNamespaceRequest.newBuilder().setNamespace(DEFAULT_NAMESPACE).setConfig(namespaceConfig).build();
      LOGGER.info("Workflow execution TTL differs for namespace " + DEFAULT_NAMESPACE + ". Changing from (" + humanReadableCurrentRetention + ") to ("
          + HUMAN_READABLE_WORKFLOW_EXECUTION_TTL + "). ");
      client.updateNamespace(updateNamespaceRequest);
    }
  }

  @FunctionalInterface
  public interface TemporalJobCreator<T extends Serializable> {

    UUID create(WorkflowClient workflowClient, long jobId, int attempt, T config);

  }

  public static WorkflowOptions getWorkflowOptionsWithWorkflowId(final TemporalJobType jobType, final String workflowId) {

    return WorkflowOptions.newBuilder()
        .setWorkflowId(workflowId)
        .setRetryOptions(NO_RETRY)
        .setTaskQueue(jobType.name())
        .build();
  }

  public static WorkflowOptions getWorkflowOptions(final TemporalJobType jobType) {
    return WorkflowOptions.newBuilder()
        .setTaskQueue(jobType.name())
        // todo (cgardens) we do not leverage Temporal retries.
        .setRetryOptions(RetryOptions.newBuilder().setMaximumAttempts(1).build())
        .build();
  }

  public static JobRunConfig createJobRunConfig(final UUID jobId, final int attemptId) {
    return createJobRunConfig(String.valueOf(jobId), attemptId);
  }

  public static JobRunConfig createJobRunConfig(final long jobId, final int attemptId) {
    return createJobRunConfig(String.valueOf(jobId), attemptId);
  }

  public static JobRunConfig createJobRunConfig(final String jobId, final int attemptId) {
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
  public static <STUB, A1, R> ImmutablePair<WorkflowExecution, CompletableFuture<R>> asyncExecute(final STUB workflowStub,
                                                                                                  final Functions.Func1<A1, R> function,
                                                                                                  final A1 arg1,
                                                                                                  final Class<R> outputType) {
    final WorkflowStub untyped = WorkflowStub.fromTyped(workflowStub);
    final WorkflowExecution workflowExecution = WorkflowClient.start(function, arg1);
    final CompletableFuture<R> resultAsync = untyped.getResultAsync(outputType);
    return ImmutablePair.of(workflowExecution, resultAsync);
  }

  /**
   * Loops and waits for the Temporal service to become available and returns a client.
   *
   * This function uses a supplier as input since the creation of a WorkflowServiceStubs can result in
   * connection exceptions as well.
   */
  public static WorkflowServiceStubs getTemporalClientWhenConnected(
                                                                    final Duration waitInterval,
                                                                    final Duration maxTimeToConnect,
                                                                    final Duration waitAfterConnection,
                                                                    final Supplier<WorkflowServiceStubs> temporalServiceSupplier) {
    LOGGER.info("Waiting for temporal server...");

    boolean temporalStatus = false;
    WorkflowServiceStubs temporalService = null;
    long millisWaited = 0;

    while (!temporalStatus) {
      if (millisWaited >= maxTimeToConnect.toMillis()) {
        throw new RuntimeException("Could not create Temporal client within max timeout!");
      }

      LOGGER.warn("Waiting for default namespace to be initialized in temporal...");
      Exceptions.toRuntime(() -> Thread.sleep(waitInterval.toMillis()));
      millisWaited = millisWaited + waitInterval.toMillis();

      try {
        temporalService = temporalServiceSupplier.get();
        temporalStatus = getNamespaces(temporalService).contains("default");
      } catch (final Exception e) {
        // Ignore the exception because this likely means that the Temporal service is still initializing.
        LOGGER.warn("Ignoring exception while trying to request Temporal namespaces:", e);
      }
    }

    // sometimes it takes a few additional seconds for workflow queue listening to be available
    Exceptions.toRuntime(() -> Thread.sleep(waitAfterConnection.toMillis()));

    LOGGER.info("Found temporal default namespace!");

    return temporalService;
  }

  protected static Set<String> getNamespaces(final WorkflowServiceStubs temporalService) {
    return temporalService.blockingStub()
        .listNamespaces(ListNamespacesRequest.newBuilder().build())
        .getNamespacesList()
        .stream()
        .map(DescribeNamespaceResponse::getNamespaceInfo)
        .map(NamespaceInfo::getName)
        .collect(toSet());
  }

  /**
   * Runs the code within the supplier while heartbeating in the backgroud. Also makes sure to shut
   * down the heartbeat server after the fact.
   */
  public static <T> T withBackgroundHeartbeat(Callable<T> callable) {
    final ScheduledExecutorService scheduledExecutor = Executors.newSingleThreadScheduledExecutor();

    try {
      scheduledExecutor.scheduleAtFixedRate(() -> {
        Activity.getExecutionContext().heartbeat(null);
      }, 0, SEND_HEARTBEAT_INTERVAL.toSeconds(), TimeUnit.SECONDS);

      return callable.call();
    } catch (final ActivityCompletionException e) {
      LOGGER.warn("Job either timed out or was cancelled.");
      throw new RuntimeException(e);
    } catch (Exception e) {
      throw new RuntimeException(e);
    } finally {
      LOGGER.info("Stopping temporal heartbeating...");
      scheduledExecutor.shutdown();
    }
  }

}
