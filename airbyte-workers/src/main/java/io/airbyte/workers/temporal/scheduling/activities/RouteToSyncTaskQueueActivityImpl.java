/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static io.airbyte.workers.temporal.trace.TemporalTraceConstants.ACTIVITY_TRACE_OPERATION_NAME;
import static io.airbyte.workers.temporal.trace.TemporalTraceConstants.Tags.CONNECTION_ID_KEY;

import datadog.trace.api.Trace;
import io.airbyte.metrics.lib.ApmTraceUtils;
import io.airbyte.workers.temporal.sync.RouterService;
import jakarta.inject.Singleton;
import java.util.Map;

@Singleton
public class RouteToSyncTaskQueueActivityImpl implements RouteToSyncTaskQueueActivity {

  private final RouterService routerService;

  public RouteToSyncTaskQueueActivityImpl(final RouterService routerService) {
    this.routerService = routerService;
  }

  @Trace(operationName = ACTIVITY_TRACE_OPERATION_NAME)
  @Override
  public RouteToSyncTaskQueueOutput route(final RouteToSyncTaskQueueInput input) {
    ApmTraceUtils.addTagsToTrace(Map.of(CONNECTION_ID_KEY, input.getConnectionId()));

    final String taskQueueForConnectionId = routerService.getTaskQueue(input.getConnectionId());

    return new RouteToSyncTaskQueueOutput(taskQueueForConnectionId);
  }

}
