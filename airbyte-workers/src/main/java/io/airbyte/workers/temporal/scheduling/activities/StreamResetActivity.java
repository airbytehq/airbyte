/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@ActivityInterface
public interface StreamResetActivity {

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class DeleteStreamResetRecordsForJobInput {

    private UUID connectionId;
    private Long jobId;

  }

  /**
   * Deletes the stream_reset record corresponding to each stream descriptor passed in
   */
  @ActivityMethod
  void deleteStreamResetRecordsForJob(DeleteStreamResetRecordsForJobInput input);

}
