/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal;

import static io.airbyte.workers.temporal.scheduling.ConnectionManagerWorkflowImpl.NON_RUNNING_JOB_ID;

import com.google.common.annotations.VisibleForTesting;
import com.google.protobuf.ByteString;
import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobDiscoverCatalogConfig;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.persistence.StreamResetPersistence;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.StreamDescriptor;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.temporal.check.connection.CheckConnectionWorkflow;
import io.airbyte.workers.temporal.discover.catalog.DiscoverCatalogWorkflow;
import io.airbyte.workers.temporal.exception.DeletedWorkflowException;
import io.airbyte.workers.temporal.exception.UnreachableWorkflowException;
import io.airbyte.workers.temporal.scheduling.ConnectionManagerWorkflow;
import io.airbyte.workers.temporal.spec.SpecWorkflow;
import io.airbyte.workers.temporal.sync.SyncWorkflow;
import io.temporal.api.workflowservice.v1.ListOpenWorkflowExecutionsRequest;
import io.temporal.api.workflowservice.v1.ListOpenWorkflowExecutionsResponse;
import io.temporal.client.WorkflowClient;
import io.temporal.serviceclient.WorkflowServiceStubs;
import java.io.IOException;
import java.nio.file.Path;
import java.time.Duration;
import java.time.Instant;
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
import org.apache.commons.lang3.time.StopWatch;

@Slf4j
public class TemporalClient {

  private final Path workspaceRoot;
  private final WorkflowClient client;
  private final WorkflowServiceStubs service;
  private final StreamResetPersistence streamResetPersistence;

  /**
   * This is use to sleep between 2 temporal queries. The query are needed to ensure that the cancel
   * and start manual sync methods wait before returning. Since temporal signals are async, we need to
   * use the queries to make sure that we are in a state in which we want to continue with.
   */
  private static final int DELAY_BETWEEN_QUERY_MS = 10;

  public TemporalClient(final WorkflowClient client,
                        final Path workspaceRoot,
                        final WorkflowServiceStubs workflowServiceStubs,
                        final StreamResetPersistence streamResetPersistence) {
    this.client = client;
    this.workspaceRoot = workspaceRoot;
    this.service = workflowServiceStubs;
    this.streamResetPersistence = streamResetPersistence;
  }

  /**
   * Direct termination of Temporal Workflows should generally be avoided. This method exists for some
   * rare circumstances where this may be required. Originally added to facilitate Airbyte's migration
   * to Temporal Cloud. TODO consider deleting this after Temporal Cloud migration
   */
  public void dangerouslyTerminateWorkflow(final String workflowId, final String reason) {
    this.client.newUntypedWorkflowStub(workflowId).terminate(reason);
  }

  public TemporalResponse<ConnectorSpecification> submitGetSpec(final UUID jobId, final int attempt, final JobGetSpecConfig config) {
    final JobRunConfig jobRunConfig = TemporalUtils.createJobRunConfig(jobId, attempt);

    final IntegrationLauncherConfig launcherConfig = new IntegrationLauncherConfig()
        .withJobId(jobId.toString())
        .withAttemptId((long) attempt)
        .withDockerImage(config.getDockerImage());
    return execute(jobRunConfig,
        () -> getWorkflowStub(SpecWorkflow.class, TemporalJobType.GET_SPEC).run(jobRunConfig, launcherConfig));

  }

  public TemporalResponse<StandardCheckConnectionOutput> submitCheckConnection(final UUID jobId,
                                                                               final int attempt,
                                                                               final JobCheckConnectionConfig config) {
    final JobRunConfig jobRunConfig = TemporalUtils.createJobRunConfig(jobId, attempt);
    final IntegrationLauncherConfig launcherConfig = new IntegrationLauncherConfig()
        .withJobId(jobId.toString())
        .withAttemptId((long) attempt)
        .withDockerImage(config.getDockerImage());
    final StandardCheckConnectionInput input = new StandardCheckConnectionInput().withConnectionConfiguration(config.getConnectionConfiguration());

    return execute(jobRunConfig,
        () -> getWorkflowStub(CheckConnectionWorkflow.class, TemporalJobType.CHECK_CONNECTION).run(jobRunConfig, launcherConfig, input));
  }

  public TemporalResponse<AirbyteCatalog> submitDiscoverSchema(final UUID jobId, final int attempt, final JobDiscoverCatalogConfig config) {
    final JobRunConfig jobRunConfig = TemporalUtils.createJobRunConfig(jobId, attempt);
    final IntegrationLauncherConfig launcherConfig = new IntegrationLauncherConfig()
        .withJobId(jobId.toString())
        .withAttemptId((long) attempt)
        .withDockerImage(config.getDockerImage());
    final StandardDiscoverCatalogInput input = new StandardDiscoverCatalogInput().withConnectionConfiguration(config.getConnectionConfiguration());

    return execute(jobRunConfig,
        () -> getWorkflowStub(DiscoverCatalogWorkflow.class, TemporalJobType.DISCOVER_SCHEMA).run(jobRunConfig, launcherConfig, input));
  }

  public TemporalResponse<StandardSyncOutput> submitSync(final long jobId, final int attempt, final JobSyncConfig config, final UUID connectionId) {
    final JobRunConfig jobRunConfig = TemporalUtils.createJobRunConfig(jobId, attempt);

    final IntegrationLauncherConfig sourceLauncherConfig = new IntegrationLauncherConfig()
        .withJobId(String.valueOf(jobId))
        .withAttemptId((long) attempt)
        .withDockerImage(config.getSourceDockerImage());

    final IntegrationLauncherConfig destinationLauncherConfig = new IntegrationLauncherConfig()
        .withJobId(String.valueOf(jobId))
        .withAttemptId((long) attempt)
        .withDockerImage(config.getDestinationDockerImage());

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
        .withDestinationResourceRequirements(config.getDestinationResourceRequirements());

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
      if (!isInRunningWorkflowCache(ConnectionManagerUtils.getConnectionManagerName(connectionId))) {
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

  private final Set<String> workflowNames = new HashSet<>();

  boolean isInRunningWorkflowCache(final String workflowName) {
    return workflowNames.contains(workflowName);
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

  /**
   * Refreshes the cache of running workflows, and returns their names. Currently called by the
   * Temporal Cloud migrator to generate a list of workflows that should be migrated. After the
   * Temporal Migration is complete, this could be removed, though it may be handy for a future use
   * case.
   */
  public Set<String> getAllRunningWorkflows() {
    final var startTime = Instant.now();
    refreshRunningWorkflow();
    final var endTime = Instant.now();
    log.info("getAllRunningWorkflows took {} milliseconds", Duration.between(startTime, endTime).toMillis());
    return workflowNames;
  }

  public ConnectionManagerWorkflow submitConnectionUpdaterAsync(final UUID connectionId) {
    log.info("Starting the scheduler temporal wf");
    final ConnectionManagerWorkflow connectionManagerWorkflow = ConnectionManagerUtils.startConnectionManagerNoSignal(client, connectionId);
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

  public void deleteConnection(final UUID connectionId) {
    try {
      ConnectionManagerUtils.signalWorkflowAndRepairIfNecessary(client, connectionId,
          connectionManagerWorkflow -> connectionManagerWorkflow::deleteConnection);
    } catch (final DeletedWorkflowException e) {
      log.info("Connection {} has already been deleted.", connectionId);
    }
  }

  public void update(final UUID connectionId) {
    final ConnectionManagerWorkflow connectionManagerWorkflow;
    try {
      connectionManagerWorkflow = ConnectionManagerUtils.getConnectionManagerWorkflow(client, connectionId);
    } catch (final DeletedWorkflowException e) {
      log.info("Connection {} is deleted, and therefore cannot be updated.", connectionId);
      return;
    } catch (final UnreachableWorkflowException e) {
      log.error(
          String.format("Failed to retrieve ConnectionManagerWorkflow for connection %s. Repairing state by creating new workflow.", connectionId),
          e);
      ConnectionManagerUtils.safeTerminateWorkflow(client, connectionId,
          "Terminating workflow in unreachable state before starting a new workflow for this connection");
      submitConnectionUpdaterAsync(connectionId);
      return;
    }

    connectionManagerWorkflow.connectionUpdated();
  }

  @Value
  @Builder
  public static class ManualOperationResult {

    final Optional<String> failingReason;
    final Optional<Long> jobId;

  }

  public ManualOperationResult startNewManualSync(final UUID connectionId) {
    log.info("Manual sync request");

    if (ConnectionManagerUtils.isWorkflowStateRunning(client, connectionId)) {
      // TODO Bmoric: Error is running
      return new ManualOperationResult(
          Optional.of("A sync is already running for: " + connectionId),
          Optional.empty());
    }

    try {
      ConnectionManagerUtils.signalWorkflowAndRepairIfNecessary(client, connectionId, workflow -> workflow::submitManualSync);
    } catch (final DeletedWorkflowException e) {
      log.error("Can't sync a deleted connection.", e);
      return new ManualOperationResult(
          Optional.of(e.getMessage()),
          Optional.empty());
    }

    do {
      try {
        Thread.sleep(DELAY_BETWEEN_QUERY_MS);
      } catch (final InterruptedException e) {
        return new ManualOperationResult(
            Optional.of("Didn't managed to start a sync for: " + connectionId),
            Optional.empty());
      }
    } while (!ConnectionManagerUtils.isWorkflowStateRunning(client, connectionId));

    log.info("end of manual schedule");

    final long jobId = ConnectionManagerUtils.getCurrentJobId(client, connectionId);

    return new ManualOperationResult(
        Optional.empty(),
        Optional.of(jobId));
  }

  public ManualOperationResult startNewCancellation(final UUID connectionId) {
    log.info("Manual cancellation request");

    final long jobId = ConnectionManagerUtils.getCurrentJobId(client, connectionId);

    try {
      ConnectionManagerUtils.signalWorkflowAndRepairIfNecessary(client, connectionId, workflow -> workflow::cancelJob);
    } catch (final DeletedWorkflowException e) {
      log.error("Can't cancel a deleted workflow", e);
      return new ManualOperationResult(
          Optional.of(e.getMessage()),
          Optional.empty());
    }

    do {
      try {
        Thread.sleep(DELAY_BETWEEN_QUERY_MS);
      } catch (final InterruptedException e) {
        return new ManualOperationResult(
            Optional.of("Didn't manage to cancel a sync for: " + connectionId),
            Optional.empty());
      }
    } while (ConnectionManagerUtils.isWorkflowStateRunning(client, connectionId));

    log.info("end of manual cancellation");

    return new ManualOperationResult(
        Optional.empty(),
        Optional.of(jobId));
  }

  public ManualOperationResult resetConnection(final UUID connectionId, final List<StreamDescriptor> streamsToReset) {
    log.info("reset sync request");

    try {
      streamResetPersistence.createStreamResets(connectionId, streamsToReset);
    } catch (final IOException e) {
      log.error("Could not persist streams to reset.", e);
      return new ManualOperationResult(
          Optional.of(e.getMessage()),
          Optional.empty());
    }

    // get the job ID before the reset, defaulting to NON_RUNNING_JOB_ID if workflow is unreachable
    final long oldJobId = ConnectionManagerUtils.getCurrentJobId(client, connectionId);

    try {
      ConnectionManagerUtils.signalWorkflowAndRepairIfNecessary(client, connectionId, workflow -> workflow::resetConnection);
    } catch (final DeletedWorkflowException e) {
      log.error("Can't reset a deleted workflow", e);
      return new ManualOperationResult(
          Optional.of(e.getMessage()),
          Optional.empty());
    }

    do {
      try {
        Thread.sleep(DELAY_BETWEEN_QUERY_MS);
      } catch (final InterruptedException e) {
        return new ManualOperationResult(
            Optional.of("Didn't manage to reset a sync for: " + connectionId),
            Optional.empty());
      }
    } while (!newJobStarted(connectionId, oldJobId));

    log.info("end of reset submission");

    final long jobId = ConnectionManagerUtils.getCurrentJobId(client, connectionId);

    return new ManualOperationResult(
        Optional.empty(),
        Optional.of(jobId));
  }

  private boolean newJobStarted(final UUID connectionId, final long oldJobId) {
    final long currentJobId = ConnectionManagerUtils.getCurrentJobId(client, connectionId);
    if (currentJobId == NON_RUNNING_JOB_ID || currentJobId == oldJobId) {
      return false;
    } else {
      return true;
    }
  }

  /**
   * This is launching a reset and wait for the reset to be performed.
   *
   * The way to do so is to wait for the jobId to change, either to a new job id or the default id
   * that signal that a workflow is waiting to be submitted
   */
  public ManualOperationResult synchronousResetConnection(final UUID connectionId, final List<StreamDescriptor> streamsToReset) {
    final ManualOperationResult resetResult = resetConnection(connectionId, streamsToReset);
    if (resetResult.getFailingReason().isPresent()) {
      return resetResult;
    }

    try {
      ConnectionManagerUtils.getConnectionManagerWorkflow(client, connectionId);
    } catch (final Exception e) {
      log.error("Encountered exception retrieving workflow after reset.", e);
      return new ManualOperationResult(
          Optional.of(e.getMessage()),
          Optional.empty());
    }

    final long oldJobId = ConnectionManagerUtils.getCurrentJobId(client, connectionId);

    do {
      try {
        Thread.sleep(DELAY_BETWEEN_QUERY_MS);
      } catch (final InterruptedException e) {
        return new ManualOperationResult(
            Optional.of("Didn't manage to reset a sync for: " + connectionId),
            Optional.empty());
      }
    } while (ConnectionManagerUtils.getCurrentJobId(client, connectionId) == oldJobId);

    log.info("End of reset");

    final long jobId = ConnectionManagerUtils.getCurrentJobId(client, connectionId);

    return new ManualOperationResult(
        Optional.empty(),
        Optional.of(jobId));
  }

  private <T> T getWorkflowStub(final Class<T> workflowClass, final TemporalJobType jobType) {
    return client.newWorkflowStub(workflowClass, TemporalUtils.getWorkflowOptions(jobType));
  }

  private <T> T getWorkflowOptionsWithWorkflowId(final Class<T> workflowClass, final TemporalJobType jobType, final String name) {
    return client.newWorkflowStub(workflowClass, TemporalUtils.getWorkflowOptionsWithWorkflowId(jobType, name));
  }

  @VisibleForTesting
  <T> TemporalResponse<T> execute(final JobRunConfig jobRunConfig, final Supplier<T> executor) {
    final Path jobRoot = WorkerUtils.getJobRoot(workspaceRoot, jobRunConfig);
    final Path logPath = WorkerUtils.getLogPath(jobRoot);

    T operationOutput = null;
    RuntimeException exception = null;

    try {
      operationOutput = executor.get();
    } catch (final RuntimeException e) {
      exception = e;
    }

    final JobMetadata metadata = new JobMetadata(exception == null, logPath);
    return new TemporalResponse<>(operationOutput, metadata);
  }

  /**
   * Check if a workflow is reachable for signal calls by attempting to query for current state. If
   * the query succeeds, and the workflow is not marked as deleted, the workflow is reachable.
   */
  @VisibleForTesting
  boolean isWorkflowReachable(final UUID connectionId) {
    try {
      ConnectionManagerUtils.getConnectionManagerWorkflow(client, connectionId);
      return true;
    } catch (final Exception e) {
      return false;
    }
  }

}
