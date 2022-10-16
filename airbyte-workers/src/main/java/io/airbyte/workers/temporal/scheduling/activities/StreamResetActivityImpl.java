/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.workers.config.WorkerMode;
import io.airbyte.workers.temporal.StreamResetRecordsHelper;
import io.micronaut.context.annotation.Requires;
import jakarta.inject.Singleton;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Singleton
@Requires(env = WorkerMode.CONTROL_PLANE)
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
