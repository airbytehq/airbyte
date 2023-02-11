/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.connectorbuilder.scheduler;

import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.temporal.TemporalJobType;
import io.airbyte.commons.temporal.TemporalResponse;
import io.airbyte.config.ConnectorJobOutput;
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
        jobReportingContext,
        () -> temporalClient.submitConnectorBuilderRead(jobId, 0, taskQueue, config),
        workspaceID);
  }

  // FIXME: copypasted
  SynchronousResponse execute(final ConnectorJobReportingContext jobContext,
                              final Supplier<TemporalResponse<StandardConnectorBuilderReadOutput>> executor,
                              final UUID workspaceId) {
    final long createdAt = Instant.now().toEpochMilli();
    final UUID jobId = jobContext.jobId();
    try {
      LOGGER.info("submitted");
      track(jobId, workspaceId, JobState.STARTED, null);
      final TemporalResponse<StandardConnectorBuilderReadOutput> temporalResponse = executor.get();
      LOGGER.info("gotresponse");
      final Optional<StandardConnectorBuilderReadOutput> jobOutput = temporalResponse.getOutput();
      final JobState outputState = temporalResponse.getMetadata().isSucceeded() ? JobState.SUCCEEDED : JobState.FAILED;

      track(jobId, workspaceId, outputState, jobOutput);

      if (outputState == JobState.FAILED && jobOutput.isPresent()) {
        reportError(jobContext, jobOutput.get(), workspaceId);
      }

      final long endedAt = Instant.now().toEpochMilli();
      return SynchronousResponse.fromTemporalResponse(
          temporalResponse,
          jobOutput.orElse(null),
          jobId,
          jobId, // FIXME: this should be config id
          createdAt,
          endedAt);
    } catch (final RuntimeException e) {
      track(jobId, workspaceId, JobState.FAILED, null);
      throw e;
    }
  }

  private <T> void track(final UUID jobId,
                         final UUID workspaceId,
                         final JobState jobState,
                         final T value) {
    jobTracker.trackConnectorBuilderRead(jobId, workspaceId,
        jobState, (StandardConnectorBuilderReadOutput) value);
  }

  private <S, T> void reportError(final ConnectorJobReportingContext jobContext,
                                  final T jobOutput,
                                  final UUID workspaceId) {
    Exceptions.swallow(() -> {
      jobErrorReporter.reportConnectorBuilderReadJobFailure(
          workspaceId,
          ((ConnectorJobOutput) jobOutput).getFailureReason(),
          jobContext);
    });
  }

}
