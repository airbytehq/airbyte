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
    return new RouteToSyncTaskQueueOutput("SOME_TASK_QUEUE");
  }
}
