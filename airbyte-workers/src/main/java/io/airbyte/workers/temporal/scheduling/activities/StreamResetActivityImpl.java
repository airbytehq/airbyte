/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.workers.temporal.StreamResetRecordsHelper;
import io.micronaut.context.annotation.Requires;
import javax.inject.Inject;
import javax.inject.Singleton;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@AllArgsConstructor
@NoArgsConstructor
@Slf4j
@Singleton
@Requires(property = "airbyte.worker.plane",
          pattern = "(?i)^(?!data_plane).*")
public class StreamResetActivityImpl implements StreamResetActivity {

  @Inject
  private StreamResetRecordsHelper streamResetRecordsHelper;

  @Override
  public void deleteStreamResetRecordsForJob(final DeleteStreamResetRecordsForJobInput input) {
    streamResetRecordsHelper.deleteStreamResetRecordsForJob(input.getJobId(), input.getConnectionId());
  }

}
