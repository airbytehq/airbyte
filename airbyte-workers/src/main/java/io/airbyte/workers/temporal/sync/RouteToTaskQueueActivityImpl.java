/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import java.util.UUID;

public class RouteToTaskQueueActivityImpl implements RouteToTaskQueueActivity {

  private final RouterService routerService;

  public RouteToTaskQueueActivityImpl(final RouterService routerService) {
    this.routerService = routerService;
  }

  @Override
  public String routeToTaskQueue(final UUID connectionId) {
    return routerService.getTaskQueue(connectionId);
  }

}
