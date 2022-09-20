/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.workers.temporal.sync.RouterService;
import javax.inject.Inject;
import javax.inject.Singleton;

@Singleton
public class RouteToSyncTaskQueueActivityImpl implements RouteToSyncTaskQueueActivity {

  @Inject
  private RouterService routerService;

  @Override
  public RouteToSyncTaskQueueOutput route(final RouteToSyncTaskQueueInput input) {
    final String taskQueueForConnectionId = routerService.getTaskQueue(input.getConnectionId());

    return new RouteToSyncTaskQueueOutput(taskQueueForConnectionId);
  }

}
