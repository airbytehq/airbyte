/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import java.time.Instant;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@ActivityInterface
public interface DisableActivity {

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class DisableActivityInput {

    private UUID connectionId;

    private Instant currTimestamp;

  }

  /**
   * Delete a connection
   */
  @ActivityMethod
  void disableConnection(DisableActivityInput input);

}
