/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.connectorbuilder.scheduler;

import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.temporal.TemporalJobType;
import io.airbyte.commons.temporal.TemporalResponse;
import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobConnectorBuilderReadConfig;
import io.airbyte.config.StandardConnectorBuilderReadOutput;
import io.airbyte.connectorbuilder.temporal.TemporalClient;
import io.airbyte.persistence.job.errorreporter.ConnectorJobReportingContext;
import io.airbyte.persistence.job.errorreporter.JobErrorReporter;
import io.airbyte.persistence.job.tracker.JobTracker;
import io.airbyte.persistence.job.tracker.JobTracker.JobState;
import java.io.IOException;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Function;
import java.util.function.Supplier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultSynchronousScheduler implements SynchronousScheduler {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultSynchronousScheduler.class);

  private final TemporalClient temporalClient;
  private final JobTracker jobTracker;
  private final JobErrorReporter jobErrorReporter;
  private final String taskQueue = TemporalJobType.CONNECTOR.name();

  public DefaultSynchronousScheduler(final TemporalClient temporalClient,
                                     final JobTracker jobTracker,
                                     final JobErrorReporter jobErrorReporter) {
    this.temporalClient = temporalClient;
    this.jobTracker = jobTracker;
    this.jobErrorReporter = jobErrorReporter;
  }

  @Override
  public SynchronousResponse<StandardConnectorBuilderReadOutput> createConnectorBuilderReadJob(UUID workspaceID, String dockerImage)
      throws IOException {

    final UUID jobId = UUID.randomUUID();
    final ConnectorJobReportingContext jobReportingContext = new ConnectorJobReportingContext(jobId, dockerImage);

    final JobConnectorBuilderReadConfig config = new JobConnectorBuilderReadConfig()
        .withDockerImage(dockerImage);

    LOGGER.info("createConnectorBuilderReadJob with" + workspaceID.toString());

    return execute(
        ConfigType.CONNECTOR_BUILDER_READ,
        jobReportingContext,
        () -> temporalClient.submitConnectorBuilderRead(jobId, 0, taskQueue, config),
        ConnectorJobOutput::getConnectorBuilderRead,
        workspaceID);
  }

  // FIXME: copypasted
  <T> SynchronousResponse<T> execute(final ConfigType configType,
                                     final ConnectorJobReportingContext jobContext,
                                     final Supplier<TemporalResponse<ConnectorJobOutput>> executor,
                                     final Function<ConnectorJobOutput, T> outputMapper,
                                     final UUID workspaceId) {
    final long createdAt = Instant.now().toEpochMilli();
    final UUID jobId = jobContext.jobId();
    try {
      LOGGER.info("submitted");
      track(jobId, configType, workspaceId, JobState.STARTED, null);
      final TemporalResponse<ConnectorJobOutput> temporalResponse = executor.get();
      LOGGER.info("gotresponse");
      final Optional<ConnectorJobOutput> jobOutput = temporalResponse.getOutput();
      final T mappedOutput = jobOutput.map(outputMapper).orElse(null);
      final JobState outputState = temporalResponse.getMetadata().isSucceeded() ? JobState.SUCCEEDED : JobState.FAILED;

      track(jobId, configType, workspaceId, outputState, mappedOutput);

      if (outputState == JobState.FAILED && jobOutput.isPresent()) {
        reportError(configType, jobContext, jobOutput.get(), workspaceId);
      }

      final long endedAt = Instant.now().toEpochMilli();
      return SynchronousResponse.fromTemporalResponse(
          temporalResponse,
          jobOutput.orElse(null),
          mappedOutput,
          jobId,
          configType,
          jobId, // FIXME: this should be config id
          createdAt,
          endedAt);
    } catch (final RuntimeException e) {
      track(jobId, configType, workspaceId, JobState.FAILED, null);
      throw e;
    }
  }

  private <T> void track(final UUID jobId,
                         final ConfigType configType,
                         final UUID workspaceId,
                         final JobState jobState,
                         final T value) {
    switch (configType) {
      case CONNECTOR_BUILDER_READ -> {
        LOGGER.info(jobId.toString());
        LOGGER.info(workspaceId.toString());
        LOGGER.info(jobState.toString());
        LOGGER.info((String) value);
        if (jobTracker != null) {
          jobTracker.trackConnectorBuilderRead(jobId, workspaceId,
              jobState, (StandardConnectorBuilderReadOutput) value);
          LOGGER.info(jobTracker.toString());
        }
      }
      default -> throw new IllegalArgumentException(
          String.format("Jobs of type %s cannot be processed here. They should be consumed in the JobSubmitter.", configType));
    }
  }

  private <S, T> void reportError(final ConfigType configType,
                                  final ConnectorJobReportingContext jobContext,
                                  final T jobOutput,
                                  final UUID workspaceId) {
    Exceptions.swallow(() -> {
      switch (configType) {
        case CONNECTOR_BUILDER_READ -> jobErrorReporter.reportConnectorBuilderReadJobFailure(
            workspaceId,
            ((ConnectorJobOutput) jobOutput).getFailureReason(),
            jobContext);
        default -> LOGGER.error("Tried to report job failure for type {}, but this job type is not supported", configType);
      }
    });
  }

}
