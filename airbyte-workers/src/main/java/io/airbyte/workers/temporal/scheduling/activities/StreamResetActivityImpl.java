/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.persistence.StreamResetPersistence;
import io.airbyte.protocol.models.StreamDescriptor;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.workers.temporal.exception.RetryableException;
import java.io.IOException;
import java.util.List;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@AllArgsConstructor
@Slf4j
public class StreamResetActivityImpl implements StreamResetActivity {

  private StreamResetPersistence streamResetPersistence;
  private JobPersistence jobPersistence;

  @Override
  public void deleteStreamResetRecordsForJob(final DeleteStreamResetRecordsForJobInput input) {
    // if there is no job, there is nothing to delete
    if (input.getJobId() == null) {
      log.info("deleteStreamResetRecordsForJob was called with a null job id; returning.");
      return;
    }

    try {
      final Job job = jobPersistence.getJob(input.getJobId());
      final ConfigType configType = job.getConfig().getConfigType();
      if (!ConfigType.RESET_CONNECTION.equals(configType)) {
        log.info("deleteStreamResetRecordsForJob was called for job {} with config type {}. Returning, as config type is not {}.",
            input.getJobId(),
            configType,
            ConfigType.RESET_CONNECTION);
        return;
      }

      final List<StreamDescriptor> resetStreams = job.getConfig().getResetConnection().getResetSourceConfiguration().getStreamsToReset();
      log.info("Deleting the following streams for reset job {} from the stream_reset table: {}", input.getJobId(), resetStreams);
      streamResetPersistence.deleteStreamResets(input.getConnectionId(), resetStreams);
    } catch (final IOException e) {
      throw new RetryableException(e);
    }
  }

}
