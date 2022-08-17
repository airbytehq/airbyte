/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.config.Configs;
import java.util.UUID;

public class DecideDataPlaneTaskQueueActivityImpl implements DecideDataPlaneTaskQueueActivity {

  private static final String AWS_DATA_PLANE_TASK_QUEUE = "AWS_DEV_SYNC_DATA_PLANE";

  private final Configs configs;

  public DecideDataPlaneTaskQueueActivityImpl(final Configs configs) {
    this.configs = configs;
  }

  @Override
  public String decideDataPlaneTaskQueue(final UUID connectionId) {
    if (configs.connectionIdsForAwsDataPlane().contains(connectionId.toString())) {
      return AWS_DATA_PLANE_TASK_QUEUE;
    }
    return configs.getDefaultDataPlaneTaskQueue();
  }

}
