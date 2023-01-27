/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal;

import static io.airbyte.commons.temporal.scheduling.ConnectionManagerWorkflow.NON_RUNNING_JOB_ID;

import com.google.common.annotations.VisibleForTesting;
import com.google.protobuf.ByteString;
import io.airbyte.commons.temporal.exception.DeletedWorkflowException;
import io.airbyte.commons.temporal.exception.UnreachableWorkflowException;
import io.airbyte.commons.temporal.scheduling.CheckConnectionWorkflow;
import io.airbyte.commons.temporal.scheduling.ConnectionManagerWorkflow;
import io.airbyte.commons.temporal.scheduling.DiscoverCatalogWorkflow;
import io.airbyte.commons.temporal.scheduling.SpecWorkflow;
import io.airbyte.commons.temporal.scheduling.SyncWorkflow;
import io.airbyte.commons.temporal.scheduling.state.WorkflowState;
import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobDiscoverCatalogConfig;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.persistence.StreamResetPersistence;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.airbyte.protocol.models.StreamDescriptor;
import io.temporal.api.common.v1.WorkflowType;
import io.temporal.api.enums.v1.WorkflowExecutionStatus;
import io.temporal.api.workflowservice.v1.ListClosedWorkflowExecutionsRequest;
import io.temporal.api.workflowservice.v1.ListClosedWorkflowExecutionsResponse;
import io.temporal.api.workflowservice.v1.ListOpenWorkflowExecutionsRequest;
import io.temporal.api.workflowservice.v1.ListOpenWorkflowExecutionsResponse;
import io.temporal.client.WorkflowClient;
import io.temporal.serviceclient.WorkflowServiceStubs;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.nio.file.Path;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import lombok.Builder;
import lombok.Value;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.time.StopWatch;

@Slf4j
@Singleton
public class TemporalClient {

  /**
   * This is used to sleep between 2 temporal queries. The query is needed to ensure that the cancel
   * and start manual sync methods wait before returning. Since temporal signals are async, we need to
   * use the queries to make sure that we are in a state in which we want to continue with.
   */
  private static final int DELAY_BETWEEN_QUERY_MS = 10;

  private final Path workspaceRoot;
  private final WorkflowClient client;
  private final WorkflowServiceStubs service;
  private final StreamResetPersistence streamResetPersistence;
  private final ConnectionManagerUtils connectionManagerUtils;
  private final StreamResetRecordsHelper streamResetRecordsHelper;

  public TemporalClient(@Named("workspaceRootTemporal") final Path workspaceRoot,
                        final WorkflowClient client,
                        final WorkflowServiceStubs service,
                        final StreamResetPersistence streamResetPersistence,
                        final ConnectionManagerUtils connectionManagerUtils,
                        final StreamResetRecordsHelper streamResetRecordsHelper) {
    this.workspaceRoot = workspaceRoot;
    this.client = client;
    this.service = service;
    this.streamResetPersistence = streamResetPersistence;
    this.connectionManagerUtils = connectionManagerUtils;
    this.streamResetRecordsHelper = streamResetRecordsHelper;
  }

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

  public Optional<WorkflowState> getWorkflowState(final UUID connectionId) {
    return connectionManagerUtils.getWorkflowState(client, connectionId);
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

  private Optional<Long> getNewJobId(final UUID connectionId, final long oldJobId) {
    final long currentJobId = connectionManagerUtils.getCurrentJobId(client, connectionId);
    if (currentJobId == NON_RUNNING_JOB_ID || currentJobId == oldJobId) {
      return Optional.empty();
    } else {
      return Optional.of(currentJobId);
    }
  }

  public TemporalResponse<ConnectorJobOutput> submitGetSpec(final UUID jobId, final int attempt, final JobGetSpecConfig config) {
    final JobRunConfig jobRunConfig = TemporalWorkflowUtils.createJobRunConfig(jobId, attempt);

    final IntegrationLauncherConfig launcherConfig = new IntegrationLauncherConfig()
        .withJobId(jobId.toString())
        .withAttemptId((long) attempt)
        .withDockerImage(config.getDockerImage())
        .withIsCustomConnector(config.getIsCustomConnector());
    return execute(jobRunConfig,
        () -> getWorkflowStub(SpecWorkflow.class, TemporalJobType.GET_SPEC).run(jobRunConfig, launcherConfig));

  }

  public TemporalResponse<ConnectorJobOutput> submitCheckConnection(final UUID jobId,
                                                                    final int attempt,
                                                                    final JobCheckConnectionConfig config) {
    final JobRunConfig jobRunConfig = TemporalWorkflowUtils.createJobRunConfig(jobId, attempt);
    final IntegrationLauncherConfig launcherConfig = new IntegrationLauncherConfig()
        .withJobId(jobId.toString())
        .withAttemptId((long) attempt)
        .withDockerImage(config.getDockerImage())
        .withProtocolVersion(config.getProtocolVersion())
        .withIsCustomConnector(config.getIsCustomConnector());
    final StandardCheckConnectionInput input = new StandardCheckConnectionInput()
        .withActorType(config.getActorType())
        .withActorId(config.getActorId())
        .withConnectionConfiguration(config.getConnectionConfiguration());

    return execute(jobRunConfig,
        () -> getWorkflowStub(CheckConnectionWorkflow.class, TemporalJobType.CHECK_CONNECTION).run(jobRunConfig, launcherConfig, input));
  }

  public TemporalResponse<ConnectorJobOutput> submitDiscoverSchema(final UUID jobId,
                                                                   final int attempt,
                                                                   final JobDiscoverCatalogConfig config) {
    final JobRunConfig jobRunConfig = TemporalWorkflowUtils.createJobRunConfig(jobId, attempt);
    final IntegrationLauncherConfig launcherConfig = new IntegrationLauncherConfig()
        .withJobId(jobId.toString())
        .withAttemptId((long) attempt)
        .withDockerImage(config.getDockerImage())
        .withProtocolVersion(config.getProtocolVersion())
        .withIsCustomConnector(config.getIsCustomConnector());
    final StandardDiscoverCatalogInput input = new StandardDiscoverCatalogInput().withConnectionConfiguration(config.getConnectionConfiguration())
        .withSourceId(config.getSourceId()).withConnectorVersion(config.getConnectorVersion()).withConfigHash(config.getConfigHash());

    return execute(jobRunConfig,
        () -> getWorkflowStub(DiscoverCatalogWorkflow.class, TemporalJobType.DISCOVER_SCHEMA).run(jobRunConfig, launcherConfig, input));
  }

  public TemporalResponse<StandardSyncOutput> submitSync(final long jobId, final int attempt, final JobSyncConfig config, final UUID connectionId) {
    final JobRunConfig jobRunConfig = TemporalWorkflowUtils.createJobRunConfig(jobId, attempt);

    final IntegrationLauncherConfig sourceLauncherConfig = new IntegrationLauncherConfig()
        .withJobId(String.valueOf(jobId))
        .withAttemptId((long) attempt)
        .withDockerImage(config.getSourceDockerImage())
        .withProtocolVersion(config.getSourceProtocolVersion())
        .withIsCustomConnector(config.getIsSourceCustomConnector());

    final IntegrationLauncherConfig destinationLauncherConfig = new IntegrationLauncherConfig()
        .withJobId(String.valueOf(jobId))
        .withAttemptId((long) attempt)
        .withDockerImage(config.getDestinationDockerImage())
        .withProtocolVersion(config.getDestinationProtocolVersion())
        .withIsCustomConnector(config.getIsDestinationCustomConnector());

    final StandardSyncInput input = new StandardSyncInput()
        .withNamespaceDefinition(config.getNamespaceDefinition())
        .withNamespaceFormat(config.getNamespaceFormat())
        .withPrefix(config.getPrefix())
        .withSourceConfiguration(config.getSourceConfiguration())
        .withDestinationConfiguration(config.getDestinationConfiguration())
        .withOperationSequence(config.getOperationSequence())
        .withCatalog(config.getConfiguredAirbyteCatalog())
        .withState(config.getState())
        .withResourceRequirements(config.getResourceRequirements())
        .withSourceResourceRequirements(config.getSourceResourceRequirements())
        .withDestinationResourceRequirements(config.getDestinationResourceRequirements())
        .withConnectionId(connectionId)
        .withWorkspaceId(config.getWorkspaceId());

    return execute(jobRunConfig,
        () -> getWorkflowStub(SyncWorkflow.class, TemporalJobType.SYNC).run(
            jobRunConfig,
            sourceLauncherConfig,
            destinationLauncherConfig,
            input,
            connectionId));
  }

  public void migrateSyncIfNeeded(final Set<UUID> connectionIds) {
    final StopWatch globalMigrationWatch = new StopWatch();
    globalMigrationWatch.start();
    refreshRunningWorkflow();

    connectionIds.forEach((connectionId) -> {
      final StopWatch singleSyncMigrationWatch = new StopWatch();
      singleSyncMigrationWatch.start();
      if (!isInRunningWorkflowCache(connectionManagerUtils.getConnectionManagerName(connectionId))) {
        log.info("Migrating: " + connectionId);
        try {
          submitConnectionUpdaterAsync(connectionId);
        } catch (final Exception e) {
          log.error("New workflow submission failed, retrying", e);
          refreshRunningWorkflow();
          submitConnectionUpdaterAsync(connectionId);
        }
      }
      singleSyncMigrationWatch.stop();
      log.info("Sync migration took: " + singleSyncMigrationWatch.formatTime());
    });
    globalMigrationWatch.stop();

    log.info("The migration to the new scheduler took: " + globalMigrationWatch.formatTime());
  }

  @VisibleForTesting
  <T> TemporalResponse<T> execute(final JobRunConfig jobRunConfig, final Supplier<T> executor) {
    final Path jobRoot = TemporalUtils.getJobRoot(workspaceRoot, jobRunConfig);
    final Path logPath = TemporalUtils.getLogPath(jobRoot);

    T operationOutput = null;
    RuntimeException exception = null;

    try {
      operationOutput = executor.get();
    } catch (final RuntimeException e) {
      exception = e;
    }

    boolean succeeded = exception == null;
    if (succeeded && operationOutput instanceof ConnectorJobOutput) {
      succeeded = getConnectorJobSucceeded((ConnectorJobOutput) operationOutput);
    }

    final JobMetadata metadata = new JobMetadata(succeeded, logPath);
    return new TemporalResponse<>(operationOutput, metadata);
  }

  private <T> T getWorkflowStub(final Class<T> workflowClass, final TemporalJobType jobType) {
    return client.newWorkflowStub(workflowClass, TemporalWorkflowUtils.buildWorkflowOptions(jobType));
  }

  public ConnectionManagerWorkflow submitConnectionUpdaterAsync(final UUID connectionId) {
    log.info("Starting the scheduler temporal wf");
    final ConnectionManagerWorkflow connectionManagerWorkflow =
        connectionManagerUtils.startConnectionManagerNoSignal(client, connectionId);
    try {
      CompletableFuture.supplyAsync(() -> {
        try {
          do {
            Thread.sleep(DELAY_BETWEEN_QUERY_MS);
          } while (!isWorkflowReachable(connectionId));
        } catch (final InterruptedException e) {}
        return null;
      }).get(60, TimeUnit.SECONDS);
    } catch (final InterruptedException | ExecutionException e) {
      log.error("Failed to create a new connection manager workflow", e);
    } catch (final TimeoutException e) {
      log.error("Can't create a new connection manager workflow due to timeout", e);
    }

    return connectionManagerWorkflow;
  }

  /**
   * This will cancel a workflow even if the connection is deleted already
   *
   * @param connectionId - connectionId to cancel
   */
  public void forceDeleteWorkflow(final UUID connectionId) {
    connectionManagerUtils.deleteWorkflowIfItExist(client, connectionId);
  }

  public void update(final UUID connectionId) {
    final ConnectionManagerWorkflow connectionManagerWorkflow;
    try {
      connectionManagerWorkflow = connectionManagerUtils.getConnectionManagerWorkflow(client, connectionId);
    } catch (final DeletedWorkflowException e) {
      log.info("Connection {} is deleted, and therefore cannot be updated.", connectionId);
      return;
    } catch (final UnreachableWorkflowException e) {
      log.error(
          String.format("Failed to retrieve ConnectionManagerWorkflow for connection %s. Repairing state by creating new workflow.", connectionId),
          e);
      connectionManagerUtils.safeTerminateWorkflow(client, connectionId,
          "Terminating workflow in unreachable state before starting a new workflow for this connection");
      submitConnectionUpdaterAsync(connectionId);
      return;
    }

    connectionManagerWorkflow.connectionUpdated();
  }

  private boolean getConnectorJobSucceeded(final ConnectorJobOutput output) {
    return output.getFailureReason() == null;
  }

  /**
   * Check if a workflow is reachable for signal calls by attempting to query for current state. If
   * the query succeeds, and the workflow is not marked as deleted, the workflow is reachable.
   */
  @VisibleForTesting
  boolean isWorkflowReachable(final UUID connectionId) {
    try {
      connectionManagerUtils.getConnectionManagerWorkflow(client, connectionId);
      return true;
    } catch (final Exception e) {
      return false;
    }
  }

  boolean isInRunningWorkflowCache(final String workflowName) {
    return workflowNames.contains(workflowName);
  }

}
