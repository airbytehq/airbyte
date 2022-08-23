/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.config.Configs;
import io.airbyte.workers.temporal.TemporalJobType;
import java.util.UUID;

public class RouteToTaskQueueActivityImpl implements RouteToTaskQueueActivity {

  // To be replaced by proper Routing Service. For now, our MVP supports a single external Data Plane
  private static final String MVP_DATA_PLANE_TASK_QUEUE = "MVP_DATA_PLANE";

  private final Configs configs;

  public RouteToTaskQueueActivityImpl(final Configs configs) {
    this.configs = configs;
  }

  @Override
  public String routeToTaskQueue(final UUID connectionId) {
    if (configs.connectionIdsForDataPlane().contains(connectionId.toString())) {
      return MVP_DATA_PLANE_TASK_QUEUE;
    }
    return TemporalJobType.SYNC.name();
  }

}
