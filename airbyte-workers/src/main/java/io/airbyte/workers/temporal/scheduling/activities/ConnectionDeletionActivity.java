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
public interface ConnectionDeletionActivity {

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class ConnectionDeletionInput {

    private UUID connectionId;

  }

  /**
   * Delete a connection
   */
  @ActivityMethod
  void deleteConnection(ConnectionDeletionInput input);

}
