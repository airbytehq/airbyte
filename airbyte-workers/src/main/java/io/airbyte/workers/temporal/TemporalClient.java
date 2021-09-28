/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobDiscoverCatalogConfig;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.WorkerUtils;
import io.temporal.client.WorkflowClient;
import java.nio.file.Path;
import java.util.UUID;
import java.util.function.Supplier;

public class TemporalClient {

  private final Path workspaceRoot;
  private final WorkflowClient client;

  public static TemporalClient production(String temporalHost, Path workspaceRoot) {
    return new TemporalClient(TemporalUtils.createTemporalClient(temporalHost), workspaceRoot);
  }

  // todo (cgardens) - there are two sources of truth on workspace root. we need to get this down to
  // one. either temporal decides and can report it or it is injected into temporal runs.
  public TemporalClient(WorkflowClient client, Path workspaceRoot) {
    this.client = client;
    this.workspaceRoot = workspaceRoot;
  }

  public TemporalResponse<ConnectorSpecification> submitGetSpec(UUID jobId, int attempt, JobGetSpecConfig config) {
    final JobRunConfig jobRunConfig = TemporalUtils.createJobRunConfig(jobId, attempt);

    final IntegrationLauncherConfig launcherConfig = new IntegrationLauncherConfig()
        .withJobId(jobId.toString())
        .withAttemptId((long) attempt)
        .withDockerImage(config.getDockerImage());
    return execute(jobRunConfig,
        () -> getWorkflowStub(SpecWorkflow.class, TemporalJobType.GET_SPEC).run(jobRunConfig, launcherConfig));

  }

  public TemporalResponse<StandardCheckConnectionOutput> submitCheckConnection(UUID jobId, int attempt, JobCheckConnectionConfig config) {
    final JobRunConfig jobRunConfig = TemporalUtils.createJobRunConfig(jobId, attempt);
    final IntegrationLauncherConfig launcherConfig = new IntegrationLauncherConfig()
        .withJobId(jobId.toString())
        .withAttemptId((long) attempt)
        .withDockerImage(config.getDockerImage());
    final StandardCheckConnectionInput input = new StandardCheckConnectionInput().withConnectionConfiguration(config.getConnectionConfiguration());

    return execute(jobRunConfig,
        () -> getWorkflowStub(CheckConnectionWorkflow.class, TemporalJobType.CHECK_CONNECTION).run(jobRunConfig, launcherConfig, input));
  }

  public TemporalResponse<AirbyteCatalog> submitDiscoverSchema(UUID jobId, int attempt, JobDiscoverCatalogConfig config) {
    final JobRunConfig jobRunConfig = TemporalUtils.createJobRunConfig(jobId, attempt);
    final IntegrationLauncherConfig launcherConfig = new IntegrationLauncherConfig()
        .withJobId(jobId.toString())
        .withAttemptId((long) attempt)
        .withDockerImage(config.getDockerImage());
    final StandardDiscoverCatalogInput input = new StandardDiscoverCatalogInput().withConnectionConfiguration(config.getConnectionConfiguration());

    return execute(jobRunConfig,
        () -> getWorkflowStub(DiscoverCatalogWorkflow.class, TemporalJobType.DISCOVER_SCHEMA).run(jobRunConfig, launcherConfig, input));
  }

  public TemporalResponse<StandardSyncOutput> submitSync(long jobId, int attempt, JobSyncConfig config) {
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
            input));
  }

  private <T> T getWorkflowStub(Class<T> workflowClass, TemporalJobType jobType) {
    return client.newWorkflowStub(workflowClass, TemporalUtils.getWorkflowOptions(jobType));
  }

  @VisibleForTesting
  <T> TemporalResponse<T> execute(JobRunConfig jobRunConfig, Supplier<T> executor) {
    final Path jobRoot = WorkerUtils.getJobRoot(workspaceRoot, jobRunConfig);
    final Path logPath = WorkerUtils.getLogPath(jobRoot);

    T operationOutput = null;
    RuntimeException exception = null;

    try {
      operationOutput = executor.get();
    } catch (RuntimeException e) {
      exception = e;
    }

    final JobMetadata metadata = new JobMetadata(exception == null, logPath);
    return new TemporalResponse<>(operationOutput, metadata);
  }

}
