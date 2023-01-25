/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.handlers;

import io.airbyte.api.model.generated.InternalOperationResult;
import io.airbyte.api.model.generated.SaveStatsRequestBody;
import io.airbyte.api.model.generated.SetWorkflowInAttemptRequestBody;
import io.airbyte.config.StreamSyncStats;
import io.airbyte.config.SyncStats;
import io.airbyte.persistence.job.JobPersistence;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Singleton
public class AttemptHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(AttemptHandler.class);

  private final JobPersistence jobPersistence;

  public AttemptHandler(final JobPersistence jobPersistence) {
    this.jobPersistence = jobPersistence;
  }

  public InternalOperationResult setWorkflowInAttempt(final SetWorkflowInAttemptRequestBody requestBody) {
    try {
      jobPersistence.setAttemptTemporalWorkflowInfo(requestBody.getJobId(),
          requestBody.getAttemptNumber(), requestBody.getWorkflowId(), requestBody.getProcessingTaskQueue());
    } catch (final IOException ioe) {
      LOGGER.error("IOException when setting temporal workflow in attempt;", ioe);
      return new InternalOperationResult().succeeded(false);
    }
    return new InternalOperationResult().succeeded(true);
  }

  public InternalOperationResult saveStats(final SaveStatsRequestBody requestBody) {
    try {
      final var stats = requestBody.getStats();
      final var streamStats = requestBody.getStreamStats().stream()
          .map(s -> new StreamSyncStats()
              .withStreamName(s.getStreamName())
              .withStreamNamespace(s.getStreamNamespace())
              .withStats(new SyncStats()
                  .withBytesEmitted(s.getStats().getBytesEmitted())
                  .withRecordsEmitted(s.getStats().getRecordsEmitted())
                  .withEstimatedBytes(s.getStats().getEstimatedBytes())
                  .withEstimatedRecords(s.getStats().getEstimatedRecords())))
          .collect(Collectors.toList());

      jobPersistence.writeStats(requestBody.getJobId(), requestBody.getAttemptNumber(),
          stats.getEstimatedRecords(), stats.getEstimatedBytes(), stats.getRecordsEmitted(), stats.getBytesEmitted(), streamStats);

    } catch (final IOException ioe) {
      LOGGER.error("IOException when setting temporal workflow in attempt;", ioe);
      return new InternalOperationResult().succeeded(false);
    }

    return new InternalOperationResult().succeeded(true);
  }

}
