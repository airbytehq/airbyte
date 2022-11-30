/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal;

import io.airbyte.commons.temporal.exception.RetryableException;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.persistence.StreamResetPersistence;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.persistence.job.models.Job;
import io.airbyte.protocol.models.StreamDescriptor;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.util.List;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;

/**
 * Helper class that provides methods for dealing with stream reset records.
 */
@Singleton
@Slf4j
public class StreamResetRecordsHelper {

  private final JobPersistence jobPersistence;
  private final StreamResetPersistence streamResetPersistence;

  public StreamResetRecordsHelper(final JobPersistence jobPersistence, final StreamResetPersistence streamResetPersistence) {
    this.jobPersistence = jobPersistence;
    this.streamResetPersistence = streamResetPersistence;
  }

  /**
   * Deletes all stream reset records related to the provided job and connection.
   *
   * @param jobId The job ID.
   * @param connectionId the connection ID.
   */
  public void deleteStreamResetRecordsForJob(final Long jobId, final UUID connectionId) {
    if (jobId == null) {
      log.info("deleteStreamResetRecordsForJob was called with a null job id; returning.");
      return;
    }

    try {
      final Job job = jobPersistence.getJob(jobId);
      final ConfigType configType = job.getConfig().getConfigType();
      if (!ConfigType.RESET_CONNECTION.equals(configType)) {
        log.info("deleteStreamResetRecordsForJob was called for job {} with config type {}. Returning, as config type is not {}.",
            jobId,
            configType,
            ConfigType.RESET_CONNECTION);
        return;
      }

      final List<StreamDescriptor> resetStreams = job.getConfig().getResetConnection().getResetSourceConfiguration().getStreamsToReset();
      log.info("Deleting the following streams for reset job {} from the stream_reset table: {}", jobId, resetStreams);
      streamResetPersistence.deleteStreamResets(connectionId, resetStreams);
    } catch (final IOException e) {
      throw new RetryableException(e);
    }
  }

}
