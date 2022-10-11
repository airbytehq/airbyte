/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal;

import com.google.common.annotations.VisibleForTesting;
import com.google.protobuf.ByteString;
import io.airbyte.commons.temporal.scheduling.ConnectionManagerWorkflow;
import io.micronaut.context.annotation.Requires;
import io.temporal.api.common.v1.WorkflowType;
import io.temporal.api.enums.v1.WorkflowExecutionStatus;
import io.temporal.api.workflowservice.v1.ListClosedWorkflowExecutionsRequest;
import io.temporal.api.workflowservice.v1.ListClosedWorkflowExecutionsResponse;
import io.temporal.api.workflowservice.v1.ListOpenWorkflowExecutionsRequest;
import io.temporal.api.workflowservice.v1.ListOpenWorkflowExecutionsResponse;
import io.temporal.client.WorkflowClient;
import io.temporal.serviceclient.WorkflowServiceStubs;
import jakarta.inject.Inject;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.NoArgsConstructor;
import lombok.Value;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;

@AllArgsConstructor
@NoArgsConstructor
@Slf4j
@Singleton
@Requires(property = "airbyte.worker.plane",
          notEquals = "DATA_PLANE")
public class TemporalClient {

  @Inject
  private WorkflowClient client;
  @Inject
  private WorkflowServiceStubs service;
  @Inject
  private ConnectionManagerUtils connectionManagerUtils;

  private final Set<String> workflowNames = new HashSet<>();

  public void restartClosedWorkflowByStatus(final WorkflowExecutionStatus executionStatus) {
    final Set<UUID> workflowExecutionInfos = fetchClosedWorkflowsByStatus(executionStatus);

    final Set<UUID> nonRunningWorkflow = filterOutRunningWorkspaceId(workflowExecutionInfos);

    nonRunningWorkflow.forEach(connectionId -> {
      connectionManagerUtils.safeTerminateWorkflow(client, connectionId, "Terminating workflow in "
          + "unreachable state before starting a new workflow for this connection");
      connectionManagerUtils.startConnectionManagerNoSignal(client, connectionId);
    });
  }

  Set<UUID> fetchClosedWorkflowsByStatus(final WorkflowExecutionStatus executionStatus) {
    ByteString token;
    ListClosedWorkflowExecutionsRequest workflowExecutionsRequest =
        ListClosedWorkflowExecutionsRequest.newBuilder()
            .setNamespace(client.getOptions().getNamespace())
            .build();

    final Set<UUID> workflowExecutionInfos = new HashSet<>();
    do {
      final ListClosedWorkflowExecutionsResponse listOpenWorkflowExecutionsRequest =
          service.blockingStub().listClosedWorkflowExecutions(workflowExecutionsRequest);
      final WorkflowType connectionManagerWorkflowType = WorkflowType.newBuilder().setName(ConnectionManagerWorkflow.class.getSimpleName()).build();
      workflowExecutionInfos.addAll(listOpenWorkflowExecutionsRequest.getExecutionsList().stream()
          .filter(workflowExecutionInfo -> workflowExecutionInfo.getType() == connectionManagerWorkflowType ||
              workflowExecutionInfo.getStatus() == executionStatus)
          .flatMap((workflowExecutionInfo -> extractConnectionIdFromWorkflowId(workflowExecutionInfo.getExecution().getWorkflowId()).stream()))
          .collect(Collectors.toSet()));
      token = listOpenWorkflowExecutionsRequest.getNextPageToken();

      workflowExecutionsRequest =
          ListClosedWorkflowExecutionsRequest.newBuilder()
              .setNamespace(client.getOptions().getNamespace())
              .setNextPageToken(token)
              .build();

    } while (token != null && token.size() > 0);

    return workflowExecutionInfos;
  }

  @VisibleForTesting
  Set<UUID> filterOutRunningWorkspaceId(final Set<UUID> workflowIds) {
    refreshRunningWorkflow();

    final Set<UUID> runningWorkflowByUUID =
        workflowNames.stream().flatMap(name -> extractConnectionIdFromWorkflowId(name).stream()).collect(Collectors.toSet());

    return workflowIds.stream().filter(workflowId -> !runningWorkflowByUUID.contains(workflowId)).collect(Collectors.toSet());
  }

  @VisibleForTesting
  void refreshRunningWorkflow() {
    workflowNames.clear();
    ByteString token;
    ListOpenWorkflowExecutionsRequest openWorkflowExecutionsRequest =
        ListOpenWorkflowExecutionsRequest.newBuilder()
            .setNamespace(client.getOptions().getNamespace())
            .build();
    do {
      final ListOpenWorkflowExecutionsResponse listOpenWorkflowExecutionsRequest =
          service.blockingStub().listOpenWorkflowExecutions(openWorkflowExecutionsRequest);
      final Set<String> workflowExecutionInfos = listOpenWorkflowExecutionsRequest.getExecutionsList().stream()
          .map((workflowExecutionInfo -> workflowExecutionInfo.getExecution().getWorkflowId()))
          .collect(Collectors.toSet());
      workflowNames.addAll(workflowExecutionInfos);
      token = listOpenWorkflowExecutionsRequest.getNextPageToken();

      openWorkflowExecutionsRequest =
          ListOpenWorkflowExecutionsRequest.newBuilder()
              .setNamespace(client.getOptions().getNamespace())
              .setNextPageToken(token)
              .build();

    } while (token != null && token.size() > 0);
  }

  Optional<UUID> extractConnectionIdFromWorkflowId(final String workflowId) {
    if (!workflowId.startsWith("connection_manager_")) {
      return Optional.empty();
    }
    return Optional.ofNullable(StringUtils.removeStart(workflowId, "connection_manager_"))
        .map(
            stringUUID -> UUID.fromString(stringUUID));
  }

  @Value
  @Builder
  public static class ManualOperationResult {

    final Optional<String> failingReason;
    final Optional<Long> jobId;
    final Optional<ErrorCode> errorCode;

  }

  public ManualOperationResult startNewManualSync(final UUID connectionId) {
    log.info("Manual sync request");

    if (connectionManagerUtils.isWorkflowStateRunning(client, connectionId)) {
      // TODO Bmoric: Error is running
      return new ManualOperationResult(
          Optional.of("A sync is already running for: " + connectionId),
          Optional.empty(), Optional.of(ErrorCode.WORKFLOW_RUNNING));
    }

    try {
      connectionManagerUtils.signalWorkflowAndRepairIfNecessary(client, connectionId, workflow -> workflow::submitManualSync);
    } catch (final DeletedWorkflowException e) {
      log.error("Can't sync a deleted connection.", e);
      return new ManualOperationResult(
          Optional.of(e.getMessage()),
          Optional.empty(), Optional.of(ErrorCode.WORKFLOW_DELETED));
    }

    do {
      try {
        Thread.sleep(DELAY_BETWEEN_QUERY_MS);
      } catch (final InterruptedException e) {
        return new ManualOperationResult(
            Optional.of("Didn't managed to start a sync for: " + connectionId),
            Optional.empty(), Optional.of(ErrorCode.UNKNOWN));
      }
    } while (!connectionManagerUtils.isWorkflowStateRunning(client, connectionId));

    log.info("end of manual schedule");

    final long jobId = connectionManagerUtils.getCurrentJobId(client, connectionId);

    return new ManualOperationResult(
        Optional.empty(),
        Optional.of(jobId), Optional.empty());
  }

  public ManualOperationResult startNewCancellation(final UUID connectionId) {
    log.info("Manual cancellation request");

    final long jobId = connectionManagerUtils.getCurrentJobId(client, connectionId);

    try {
      connectionManagerUtils.signalWorkflowAndRepairIfNecessary(client, connectionId, workflow -> workflow::cancelJob);
    } catch (final DeletedWorkflowException e) {
      log.error("Can't cancel a deleted workflow", e);
      return new ManualOperationResult(
          Optional.of(e.getMessage()),
          Optional.empty(), Optional.of(ErrorCode.WORKFLOW_DELETED));
    }

    do {
      try {
        Thread.sleep(DELAY_BETWEEN_QUERY_MS);
      } catch (final InterruptedException e) {
        return new ManualOperationResult(
            Optional.of("Didn't manage to cancel a sync for: " + connectionId),
            Optional.empty(), Optional.of(ErrorCode.UNKNOWN));
      }
    } while (connectionManagerUtils.isWorkflowStateRunning(client, connectionId));

    streamResetRecordsHelper.deleteStreamResetRecordsForJob(jobId, connectionId);

    log.info("end of manual cancellation");

    return new ManualOperationResult(
        Optional.empty(),
        Optional.of(jobId), Optional.empty());
  }

  public ManualOperationResult resetConnection(final UUID connectionId,
                                               final List<StreamDescriptor> streamsToReset,
                                               final boolean syncImmediatelyAfter) {
    log.info("reset sync request");

    try {
      streamResetPersistence.createStreamResets(connectionId, streamsToReset);
    } catch (final IOException e) {
      log.error("Could not persist streams to reset.", e);
      return new ManualOperationResult(
          Optional.of(e.getMessage()),
          Optional.empty(), Optional.of(ErrorCode.UNKNOWN));
    }

    // get the job ID before the reset, defaulting to NON_RUNNING_JOB_ID if workflow is unreachable
    final long oldJobId = connectionManagerUtils.getCurrentJobId(client, connectionId);

    try {
      if (syncImmediatelyAfter) {
        connectionManagerUtils.signalWorkflowAndRepairIfNecessary(client, connectionId, workflow -> workflow::resetConnectionAndSkipNextScheduling);
      } else {
        connectionManagerUtils.signalWorkflowAndRepairIfNecessary(client, connectionId, workflow -> workflow::resetConnection);
      }
    } catch (final DeletedWorkflowException e) {
      log.error("Can't reset a deleted workflow", e);
      return new ManualOperationResult(
          Optional.of(e.getMessage()),
          Optional.empty(), Optional.of(ErrorCode.UNKNOWN));
    }

    Optional<Long> newJobId;

    do {
      try {
        Thread.sleep(DELAY_BETWEEN_QUERY_MS);
      } catch (final InterruptedException e) {
        return new ManualOperationResult(
            Optional.of("Didn't manage to reset a sync for: " + connectionId),
            Optional.empty(), Optional.of(ErrorCode.UNKNOWN));
      }
      newJobId = getNewJobId(connectionId, oldJobId);
    } while (newJobId.isEmpty());

    log.info("end of reset submission");

    return new ManualOperationResult(
        Optional.empty(),
        newJobId, Optional.empty());
  }
}
