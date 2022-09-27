/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.workers.temporal.StreamResetRecordsHelper;
import io.micronaut.context.annotation.Requires;
import javax.inject.Singleton;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Singleton
@Requires(property = "airbyte.worker.plane",
          pattern = "(?i)^(?!data_plane).*")
public class StreamResetActivityImpl implements StreamResetActivity {

  private final StreamResetRecordsHelper streamResetRecordsHelper;

  public StreamResetActivityImpl(final StreamResetRecordsHelper streamResetRecordsHelper) {
    this.streamResetRecordsHelper = streamResetRecordsHelper;
  }

  @Override
  public void deleteStreamResetRecordsForJob(final DeleteStreamResetRecordsForJobInput input) {
    streamResetRecordsHelper.deleteStreamResetRecordsForJob(input.getJobId(), input.getConnectionId());
  }

}
