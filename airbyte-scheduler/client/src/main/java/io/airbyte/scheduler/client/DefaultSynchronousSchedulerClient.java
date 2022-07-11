/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.client;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.FailureReason;
import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobDiscoverCatalogConfig;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardDiscoverCatalogOutput;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.persistence.job_factory.OAuthConfigSupplier;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker.JobState;
import io.airbyte.workers.JobStatus;
import io.airbyte.workers.OutputAndStatus;
import io.airbyte.workers.temporal.TemporalClient;
import io.airbyte.workers.temporal.TemporalResponse;
import java.io.IOException;
import java.time.Instant;
import java.util.UUID;
import java.util.function.Function;
import javax.annotation.Nullable;

public class DefaultSynchronousSchedulerClient implements SynchronousSchedulerClient {

  private final TemporalClient temporalClient;
  private final JobTracker jobTracker;
  private final OAuthConfigSupplier oAuthConfigSupplier;

  public DefaultSynchronousSchedulerClient(final TemporalClient temporalClient,
                                           final JobTracker jobTracker,
                                           final OAuthConfigSupplier oAuthConfigSupplier) {
    this.temporalClient = temporalClient;
    this.jobTracker = jobTracker;
    this.oAuthConfigSupplier = oAuthConfigSupplier;
  }

  @Override
  public SynchronousResponse<StandardCheckConnectionOutput> createSourceCheckConnectionJob(final SourceConnection source, final String dockerImage)
      throws IOException {
    final JsonNode sourceConfiguration = oAuthConfigSupplier.injectSourceOAuthParameters(
        source.getSourceDefinitionId(),
        source.getWorkspaceId(),
        source.getConfiguration());
    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig()
        .withConnectionConfiguration(sourceConfiguration)
        .withDockerImage(dockerImage);

    return execute(
        ConfigType.CHECK_CONNECTION_SOURCE,
        source.getSourceDefinitionId(),
        jobId -> temporalClient.submitCheckConnection(UUID.randomUUID(), 0, jobCheckConnectionConfig),
        source.getWorkspaceId());
  }

  @Override
  public SynchronousResponse<StandardCheckConnectionOutput> createDestinationCheckConnectionJob(final DestinationConnection destination,
                                                                                                final String dockerImage)
      throws IOException {
    final JsonNode destinationConfiguration = oAuthConfigSupplier.injectDestinationOAuthParameters(
        destination.getDestinationDefinitionId(),
        destination.getWorkspaceId(),
        destination.getConfiguration());
    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig()
        .withConnectionConfiguration(destinationConfiguration)
        .withDockerImage(dockerImage);

    return execute(
        ConfigType.CHECK_CONNECTION_DESTINATION,
        destination.getDestinationDefinitionId(),
        jobId -> temporalClient.submitCheckConnection(UUID.randomUUID(), 0, jobCheckConnectionConfig),
        destination.getWorkspaceId());
  }

  @Override
  public SynchronousResponse<StandardDiscoverCatalogOutput> createDiscoverSchemaJob(final SourceConnection source, final String dockerImage)
      throws IOException {
    final JsonNode sourceConfiguration = oAuthConfigSupplier.injectSourceOAuthParameters(
        source.getSourceDefinitionId(),
        source.getWorkspaceId(),
        source.getConfiguration());
    final JobDiscoverCatalogConfig jobDiscoverCatalogConfig = new JobDiscoverCatalogConfig()
        .withConnectionConfiguration(sourceConfiguration)
        .withDockerImage(dockerImage);

    return execute(
        ConfigType.DISCOVER_SCHEMA,
        source.getSourceDefinitionId(),
        jobId -> temporalClient.submitDiscoverSchema(UUID.randomUUID(), 0, jobDiscoverCatalogConfig),
        source.getWorkspaceId());
  }

  @Override
  public SynchronousResponse<ConnectorSpecification> createGetSpecJob(final String dockerImage) throws IOException {
    final JobGetSpecConfig jobSpecConfig = new JobGetSpecConfig().withDockerImage(dockerImage);

    return execute(
        ConfigType.GET_SPEC,
        null,
        jobId -> temporalClient.submitGetSpec(UUID.randomUUID(), 0, jobSpecConfig),
        null);
  }

  private <T> OutputAndStatus<T> toOutputAndStatus(final ConfigType configType, final TemporalResponse<T> response) {
    final JobStatus status;
    if (!response.isSuccess()) {
      status = JobStatus.FAILED;
    } else {
      final FailureReason failureReason;
      switch (configType) {
        case DISCOVER_SCHEMA:
          failureReason = ((StandardDiscoverCatalogOutput) response.getOutput().orElseThrow()).getFailureReason();
          break;
        // TODO others
        default:
          failureReason = null;
      }

      if (failureReason != null) {
        status = JobStatus.FAILED;
      } else {
        status = JobStatus.SUCCEEDED;
      }
    }
    return new OutputAndStatus<>(status, response.getOutput().orElse(null));
  }

  @VisibleForTesting
  <T> SynchronousResponse<T> execute(final ConfigType configType,
                                     @Nullable final UUID connectorDefinitionId,
                                     final Function<UUID, TemporalResponse<T>> executor,
                                     final UUID workspaceId) {
    final long createdAt = Instant.now().toEpochMilli();
    final UUID jobId = UUID.randomUUID();
    try {
      track(jobId, configType, connectorDefinitionId, workspaceId, JobState.STARTED, null);
      final TemporalResponse<T> operationOutput = executor.apply(jobId);
      final OutputAndStatus<T> outputAndStatus = toOutputAndStatus(configType, operationOutput);
      final JobState outputState = outputAndStatus.getStatus() == JobStatus.SUCCEEDED ? JobState.SUCCEEDED : JobState.FAILED;
      track(jobId, configType, connectorDefinitionId, workspaceId, outputState, operationOutput.getOutput().orElse(null));
      reportJob(configType, outputAndStatus);
      final long endedAt = Instant.now().toEpochMilli();

      if (outputState == JobState.FAILED) {
        throw new RuntimeException("Job failed");
      }

      final SynchronousResponse<T> synchronousResponse = SynchronousResponse.fromTemporalResponse(
          operationOutput,
          jobId,
          configType,
          connectorDefinitionId,
          createdAt,
          endedAt);

      // TODO make this a part of the SynchronousResponse creation
      synchronousResponse.setJobStatus(outputAndStatus.getStatus());

      return synchronousResponse;
    } catch (final RuntimeException e) {
      track(jobId, configType, connectorDefinitionId, workspaceId, JobState.FAILED, null);
      throw e;
    }
  }

  private <T> void reportJob(final ConfigType configType, final OutputAndStatus<T> outputAndStatus) {
    if (outputAndStatus.getStatus() == JobStatus.FAILED) {
      // TODO send this to the job error reporter
      // JobErrorReporter.reportJobFailure();
    }

  }

  /**
   * @param connectorDefinitionId either source or destination definition id
   */
  private <T> void track(final UUID jobId,
                         final ConfigType configType,
                         final UUID connectorDefinitionId,
                         final UUID workspaceId,
                         final JobState jobState,
                         final T value) {
    switch (configType) {
      case CHECK_CONNECTION_SOURCE -> jobTracker.trackCheckConnectionSource(
          jobId,
          connectorDefinitionId,
          workspaceId,
          jobState,
          (StandardCheckConnectionOutput) value);
      case CHECK_CONNECTION_DESTINATION -> jobTracker.trackCheckConnectionDestination(
          jobId,
          connectorDefinitionId,
          workspaceId,
          jobState,
          (StandardCheckConnectionOutput) value);
      case DISCOVER_SCHEMA -> jobTracker.trackDiscover(jobId, connectorDefinitionId, workspaceId, jobState);
      case GET_SPEC -> {
        // skip tracking for get spec to avoid noise.
      }
      default -> throw new IllegalArgumentException(
          String.format("Jobs of type %s cannot be processed here. They should be consumed in the JobSubmitter.", configType));
    }

  }

}
