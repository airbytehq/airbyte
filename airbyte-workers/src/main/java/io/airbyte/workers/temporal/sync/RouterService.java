/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.config.Configs;
import io.airbyte.workers.temporal.TemporalJobType;
import java.util.UUID;
import lombok.AllArgsConstructor;

@AllArgsConstructor
public class RouterService {

  private static final String MVP_DATA_PLANE_TASK_QUEUE = "MVP_DATA_PLANE";

  private final Configs configs;

  /**
   * For now, returns a Task Queue by checking to see if the connectionId is on the env var list for
   * usage in the MVP Data Plane. This will be replaced by a proper Router Service in the future.
   */
  public String getTaskQueue(final UUID connectionId) {
    if (configs.connectionIdsForMvpDataPlane().contains(connectionId.toString())) {
      return MVP_DATA_PLANE_TASK_QUEUE;
    }
    return TemporalJobType.SYNC.name();
  }

}
