/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.api.model.ConnectionUpdate;
import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobDiscoverCatalogConfig;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.temporal.check.connection.CheckConnectionWorkflow;
import io.airbyte.workers.temporal.discover.catalog.DiscoverCatalogWorkflow;
import io.airbyte.workers.temporal.scheduling.ConnectionUpdaterInput;
import io.airbyte.workers.temporal.scheduling.ConnectionUpdaterWorkflow;
import io.airbyte.workers.temporal.scheduling.state.WorkflowState;
import io.airbyte.workers.temporal.spec.SpecWorkflow;
import io.airbyte.workers.temporal.sync.SyncWorkflow;
import io.temporal.api.workflow.v1.WorkflowExecutionInfo;
import io.temporal.api.workflowservice.v1.ListOpenWorkflowExecutionsRequest;
import io.temporal.api.workflowservice.v1.ListOpenWorkflowExecutionsResponse;
import io.temporal.client.BatchRequest;
import io.temporal.client.WorkflowClient;
import io.temporal.serviceclient.WorkflowServiceStubs;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import lombok.Value;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class TemporalClient {

  private final Path workspaceRoot;
  private final WorkflowClient client;
  private final WorkflowServiceStubs service;

  public static TemporalClient production(final String temporalHost, final Path workspaceRoot) {
    return new TemporalClient(TemporalUtils.createTemporalClient(temporalHost), workspaceRoot, TemporalUtils.createTemporalService(temporalHost));
  }

  // todo (cgardens) - there are two sources of truth on workspace root. we need to get this down to
  // one. either temporal decides and can report it or it is injected into temporal runs.
  public TemporalClient(final WorkflowClient client,
                        final Path workspaceRoot,
                        final WorkflowServiceStubs workflowServiceStubs) {
    this.client = client;
    this.workspaceRoot = workspaceRoot;
    this.service = workflowServiceStubs;
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
        .withResourceRequirements(config.getResourceRequirements());

    return execute(jobRunConfig,
        () -> getWorkflowStub(SyncWorkflow.class, TemporalJobType.SYNC).run(
            jobRunConfig,
            sourceLauncherConfig,
            destinationLauncherConfig,
            input,
            connectionId));
  }

  public void submitConnectionUpdaterAsync(final UUID connectionId) {
    log.info("Starting the scheduler temporal wf");
    final ConnectionUpdaterWorkflow connectionUpdaterWorkflow = getWorkflowOptionsWithWorkflowId(ConnectionUpdaterWorkflow.class,
        TemporalJobType.CONNECTION_UPDATER, "connection_updater_" + connectionId);
    final BatchRequest signalRequest = client.newSignalWithStartRequest();
    final ConnectionUpdaterInput input = new ConnectionUpdaterInput(connectionId, null, null, false, 1, null);
    signalRequest.add(connectionUpdaterWorkflow::run, input);

    final ExecutorService threadpool = Executors.newCachedThreadPool();

    final Future<Void> futureTask = threadpool.submit(() -> {
      connectionUpdaterWorkflow.run(input);

      return null;
    });
    log.info("Scheduler temporal wf started");
  }

  public void deleteConnection(final UUID connectionId) {
    final ConnectionUpdaterWorkflow connectionUpdaterWorkflow = getConnectionUpdateWorkflow(connectionId);

    connectionUpdaterWorkflow.deleteConnection();
  }

  public void update(final ConnectionUpdate connectionUpdate) throws JsonValidationException, ConfigNotFoundException, IOException {
    final ConnectionUpdaterWorkflow connectionUpdaterWorkflow = getConnectionUpdateWorkflow(connectionUpdate.getConnectionId());

    connectionUpdaterWorkflow.connectionUpdated();
  }

  @Value
  public class ManualSyncSubmissionResult {

    final Optional<String> failingReason;
    final Optional<Long> jobId;

  }

  public ManualSyncSubmissionResult startNewManualSync(final UUID connectionId) {
    log.info("Manual sync request");
    final List<WorkflowExecutionInfo> workflows = getExecutionsResponse("connection_updater_" + connectionId);

    if (workflows.isEmpty()) {
      return new ManualSyncSubmissionResult(
          Optional.of("No scheduler workflow is running for: " + connectionId),
          Optional.empty());
    }

    final ConnectionUpdaterWorkflow connectionUpdaterWorkflow =
        getExistingWorkflow(ConnectionUpdaterWorkflow.class, "connection_updater_" + connectionId);
    final WorkflowState workflowState = connectionUpdaterWorkflow.getState();

    if (workflowState.isRunning()) {
      // TODO Bmoric: Error is running
      return new ManualSyncSubmissionResult(
          Optional.of("A sync is already running for: " + connectionId),
          Optional.empty());
    }

    connectionUpdaterWorkflow.submitManualSync();

    do {
      try {
        Thread.sleep(10);
      } catch (final InterruptedException e) {
        return new ManualSyncSubmissionResult(
            Optional.of("Didn't managed to start a sync for: " + connectionId),
            Optional.empty());
      }
    } while (!connectionUpdaterWorkflow.getState().isRunning());

    log.info("end of manual schedule");

    final long jobId = connectionUpdaterWorkflow.getJobInformation().getJobId();

    return new ManualSyncSubmissionResult(
        Optional.empty(),
        Optional.of(jobId));
  }

  @Value
  public class NewCancellationSubmissionResult {

    final Optional<String> failingReason;
    final Optional<Long> jobId;

  }

  public ManualSyncSubmissionResult startNewCancelation(final UUID connectionId) {
    log.info("Manual sync request");

    final List<WorkflowExecutionInfo> workflows = getExecutionsResponse("connection_updater_" + connectionId);

    if (workflows.isEmpty()) {
      return new ManualSyncSubmissionResult(
          Optional.of("No scheduler workflow is running for: " + connectionId),
          Optional.empty());
    }

    final ConnectionUpdaterWorkflow connectionUpdaterWorkflow =
        getExistingWorkflow(ConnectionUpdaterWorkflow.class, "connection_updater_" + connectionId);

    connectionUpdaterWorkflow.cancelJob();

    do {
      try {
        Thread.sleep(10);
      } catch (final InterruptedException e) {
        return new ManualSyncSubmissionResult(
            Optional.of("Didn't manage cancel a sync for: " + connectionId),
            Optional.empty());
      }
    } while (connectionUpdaterWorkflow.getState().isRunning());

    log.info("end of manual schedule");

    final long jobId = connectionUpdaterWorkflow.getJobInformation().getJobId();

    return new ManualSyncSubmissionResult(
        Optional.empty(),
        Optional.of(jobId));
  }

  private <T> T getWorkflowStub(final Class<T> workflowClass, final TemporalJobType jobType) {
    return client.newWorkflowStub(workflowClass, TemporalUtils.getWorkflowOptions(jobType));
  }

  private <T> T getWorkflowOptionsWithWorkflowId(final Class<T> workflowClass, final TemporalJobType jobType, final String name) {
    return client.newWorkflowStub(workflowClass, TemporalUtils.getWorkflowOptionsWithWorkflowId(jobType, name));
  }

  private <T> T getExistingWorkflow(final Class<T> workflowClass, final String name) {
    return client.newWorkflowStub(workflowClass, name);
  }

  private ConnectionUpdaterWorkflow getConnectionUpdateWorkflow(final UUID connectionId) {
    final List<WorkflowExecutionInfo> workflows = getExecutionsResponse("connection_updater_" + connectionId);

    if (workflows.isEmpty()) {
      throw new IllegalStateException("No running workflow for the connection {} while trying to delete it");
    }

    final ConnectionUpdaterWorkflow connectionUpdaterWorkflow =
        getExistingWorkflow(ConnectionUpdaterWorkflow.class, "connection_updater_" + connectionId);

    return connectionUpdaterWorkflow;
  }

  @VisibleForTesting <T> TemporalResponse<T> execute(final JobRunConfig jobRunConfig, final Supplier<T> executor) {
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

  public List<WorkflowExecutionInfo> getExecutionsResponse(final String workflowName) {
    // TODO: pagination as explained here: https://temporalio.slack.com/archives/CTRCR8RBP/p1638926310308200
    final ListOpenWorkflowExecutionsRequest openWorkflowExecutionsRequest =
        ListOpenWorkflowExecutionsRequest.newBuilder()
            .setNamespace(client.getOptions().getNamespace())
            .build();
    final ListOpenWorkflowExecutionsResponse listOpenWorkflowExecutionsRequest =
        service.blockingStub().listOpenWorkflowExecutions(openWorkflowExecutionsRequest);

    final List<WorkflowExecutionInfo> workflowExecutionInfos = listOpenWorkflowExecutionsRequest.getExecutionsList().stream()
        .filter((workflowExecutionInfo -> workflowExecutionInfo.getExecution().getWorkflowId().equals(workflowName)))
        .collect(Collectors.toList());

    return workflowExecutionInfos;
  }

}
