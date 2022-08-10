/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.client;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobDiscoverCatalogConfig;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.persistence.job_error_reporter.ConnectorJobReportingContext;
import io.airbyte.scheduler.persistence.job_error_reporter.JobErrorReporter;
import io.airbyte.scheduler.persistence.job_factory.OAuthConfigSupplier;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker.JobState;
import io.airbyte.workers.temporal.TemporalClient;
import io.airbyte.workers.temporal.TemporalResponse;
import java.io.IOException;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Function;
import java.util.function.Supplier;
import javax.annotation.Nullable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultSynchronousSchedulerClient implements SynchronousSchedulerClient {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultSynchronousSchedulerClient.class);

  private final TemporalClient temporalClient;
  private final JobTracker jobTracker;
  private final JobErrorReporter jobErrorReporter;
  private final OAuthConfigSupplier oAuthConfigSupplier;

  public DefaultSynchronousSchedulerClient(final TemporalClient temporalClient,
                                           final JobTracker jobTracker,
                                           final JobErrorReporter jobErrorReporter,
                                           final OAuthConfigSupplier oAuthConfigSupplier) {
    this.temporalClient = temporalClient;
    this.jobTracker = jobTracker;
    this.jobErrorReporter = jobErrorReporter;
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

    final UUID jobId = UUID.randomUUID();
    final ConnectorJobReportingContext jobReportingContext = new ConnectorJobReportingContext(jobId, dockerImage);

    return execute(
        ConfigType.CHECK_CONNECTION_SOURCE,
        jobReportingContext,
        source.getSourceDefinitionId(),
        () -> temporalClient.submitCheckConnection(UUID.randomUUID(), 0, jobCheckConnectionConfig),
        ConnectorJobOutput::getCheckConnection,
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

    final UUID jobId = UUID.randomUUID();
    final ConnectorJobReportingContext jobReportingContext = new ConnectorJobReportingContext(jobId, dockerImage);

    return execute(
        ConfigType.CHECK_CONNECTION_DESTINATION,
        jobReportingContext,
        destination.getDestinationDefinitionId(),
        () -> temporalClient.submitCheckConnection(jobId, 0, jobCheckConnectionConfig),
        ConnectorJobOutput::getCheckConnection,
        destination.getWorkspaceId());
  }

  @Override
  public SynchronousResponse<AirbyteCatalog> createDiscoverSchemaJob(final SourceConnection source, final String dockerImage)
      throws IOException {
    final JsonNode sourceConfiguration = oAuthConfigSupplier.injectSourceOAuthParameters(
        source.getSourceDefinitionId(),
        source.getWorkspaceId(),
        source.getConfiguration());
    final JobDiscoverCatalogConfig jobDiscoverCatalogConfig = new JobDiscoverCatalogConfig()
        .withConnectionConfiguration(sourceConfiguration)
        .withDockerImage(dockerImage);

    final UUID jobId = UUID.randomUUID();
    final ConnectorJobReportingContext jobReportingContext = new ConnectorJobReportingContext(jobId, dockerImage);

    return execute(
        ConfigType.DISCOVER_SCHEMA,
        jobReportingContext,
        source.getSourceDefinitionId(),
        () -> temporalClient.submitDiscoverSchema(jobId, 0, jobDiscoverCatalogConfig),
        ConnectorJobOutput::getDiscoverCatalog,
        source.getWorkspaceId());
  }

  @Override
  public SynchronousResponse<ConnectorSpecification> createGetSpecJob(final String dockerImage) throws IOException {
    final JobGetSpecConfig jobSpecConfig = new JobGetSpecConfig().withDockerImage(dockerImage);

    final UUID jobId = UUID.randomUUID();
    final ConnectorJobReportingContext jobReportingContext = new ConnectorJobReportingContext(jobId, dockerImage);

    return execute(
        ConfigType.GET_SPEC,
        jobReportingContext,
        null,
        () -> temporalClient.submitGetSpec(jobId, 0, jobSpecConfig),
        ConnectorJobOutput::getSpec,
        null);
  }

  @VisibleForTesting
  <T, U> SynchronousResponse<T> execute(final ConfigType configType,
                                        final ConnectorJobReportingContext jobContext,
                                        @Nullable final UUID connectorDefinitionId,
                                        final Supplier<TemporalResponse<U>> executor,
                                        final Function<U, T> outputMapper,
                                        final UUID workspaceId) {
    final long createdAt = Instant.now().toEpochMilli();
    final UUID jobId = jobContext.jobId();
    try {
      track(jobId, configType, connectorDefinitionId, workspaceId, JobState.STARTED, null);
      final TemporalResponse<U> temporalResponse = executor.get();
      final Optional<U> jobOutput = temporalResponse.getOutput();
      final T mappedOutput = jobOutput.map(outputMapper).orElse(null);
      final JobState outputState = temporalResponse.getMetadata().isSucceeded() ? JobState.SUCCEEDED : JobState.FAILED;

      track(jobId, configType, connectorDefinitionId, workspaceId, outputState, mappedOutput);

      if (outputState == JobState.FAILED && jobOutput.isPresent()) {
        reportError(configType, jobContext, jobOutput.get(), connectorDefinitionId, workspaceId);
      }

      final long endedAt = Instant.now().toEpochMilli();
      return SynchronousResponse.fromTemporalResponse(
          temporalResponse,
          mappedOutput,
          jobId,
          configType,
          connectorDefinitionId,
          createdAt,
          endedAt);
    } catch (final RuntimeException e) {
      track(jobId, configType, connectorDefinitionId, workspaceId, JobState.FAILED, null);
      throw e;
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

  private <S, T> void reportError(final ConfigType configType,
                                  final ConnectorJobReportingContext jobContext,
                                  final T jobOutput,
                                  final UUID connectorDefinitionId,
                                  final UUID workspaceId) {
    Exceptions.swallow(() -> {
      switch (configType) {
        case CHECK_CONNECTION_SOURCE -> jobErrorReporter.reportSourceCheckJobFailure(
            connectorDefinitionId,
            workspaceId,
            ((ConnectorJobOutput) jobOutput).getFailureReason(),
            jobContext);
        case CHECK_CONNECTION_DESTINATION -> jobErrorReporter.reportDestinationCheckJobFailure(
            connectorDefinitionId,
            workspaceId,
            ((ConnectorJobOutput) jobOutput).getFailureReason(),
            jobContext);
        case DISCOVER_SCHEMA -> jobErrorReporter.reportDiscoverJobFailure(
            connectorDefinitionId,
            workspaceId,
            ((ConnectorJobOutput) jobOutput).getFailureReason(),
            jobContext);
        case GET_SPEC -> jobErrorReporter.reportSpecJobFailure(
            ((ConnectorJobOutput) jobOutput).getFailureReason(),
            jobContext);
        default -> LOGGER.error("Tried to report job failure for type {}, but this job type is not supported", configType);
      }
    });
  }

}
