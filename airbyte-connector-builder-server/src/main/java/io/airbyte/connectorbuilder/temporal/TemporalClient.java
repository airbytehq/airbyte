/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.connectorbuilder.temporal;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.temporal.ConnectionManagerUtils;
import io.airbyte.commons.temporal.JobMetadata;
import io.airbyte.commons.temporal.StreamResetRecordsHelper;
import io.airbyte.commons.temporal.TemporalResponse;
import io.airbyte.commons.temporal.TemporalUtils;
import io.airbyte.commons.temporal.TemporalWorkflowUtils;
import io.airbyte.commons.temporal.scheduling.ConnectorBuilderReadWorkflow;
import io.airbyte.config.JobConnectorBuilderReadConfig;
import io.airbyte.config.StandardConnectorBuilderReadInput;
import io.airbyte.config.StandardConnectorBuilderReadOutput;
import io.airbyte.config.persistence.StreamResetPersistence;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.temporal.client.WorkflowClient;
import io.temporal.serviceclient.WorkflowServiceStubs;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.nio.file.Path;
import java.util.UUID;
import java.util.function.Supplier;
import lombok.extern.slf4j.Slf4j;

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

  public TemporalResponse<StandardConnectorBuilderReadOutput> submitConnectorBuilderRead(final UUID jobId,
                                                                                         final int attempt,
                                                                                         final String taskQueue,
                                                                                         final JobConnectorBuilderReadConfig config) {
    final JobRunConfig jobRunConfig = TemporalWorkflowUtils.createJobRunConfig(jobId, attempt);
    final StandardConnectorBuilderReadInput input = new StandardConnectorBuilderReadInput()
        .withDockerImage(config.getDockerImage());
    return execute(jobRunConfig,
        () -> getWorkflowStubWithTaskQueue(ConnectorBuilderReadWorkflow.class, taskQueue).run(jobRunConfig, input));
  }

  // Copied from airbyte-temporal
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
    if (succeeded && operationOutput instanceof StandardConnectorBuilderReadOutput) {
      succeeded = getConnectorJobSucceeded((StandardConnectorBuilderReadOutput) operationOutput);
    }

    final JobMetadata metadata = new JobMetadata(succeeded, logPath);
    return new TemporalResponse<>(operationOutput, metadata);
  }

  private <T> T getWorkflowStubWithTaskQueue(final Class<T> workflowClass, final String taskQueue) {
    return client.newWorkflowStub(workflowClass, TemporalWorkflowUtils.buildWorkflowOptionsWithTaskQueue(taskQueue));
  }

  private boolean getConnectorJobSucceeded(final StandardConnectorBuilderReadOutput output) {
    // return output.getFailureReason() == null; FIXME
    return true;
  }

}
