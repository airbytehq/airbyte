/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.workers.temporal.sync.RouterService;
import jakarta.inject.Singleton;

@Singleton
public class RouteToSyncTaskQueueActivityImpl implements RouteToSyncTaskQueueActivity {

  private final RouterService routerService;

  public RouteToSyncTaskQueueActivityImpl(final RouterService routerService) {
    this.routerService = routerService;
  }

  @Override
  public RouteToSyncTaskQueueOutput route(final RouteToSyncTaskQueueInput input) {
    final String taskQueueForConnectionId = routerService.getTaskQueue(input.getConnectionId());

    return new RouteToSyncTaskQueueOutput(taskQueueForConnectionId);
  }

}
