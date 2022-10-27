/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static io.airbyte.metrics.lib.ApmTraceConstants.ACTIVITY_TRACE_OPERATION_NAME;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.CONNECTION_ID_KEY;

import datadog.trace.api.Trace;
import io.airbyte.commons.temporal.exception.RetryableException;
import io.airbyte.metrics.lib.ApmTraceUtils;
import io.airbyte.workers.temporal.scheduling.RouterService;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.util.Map;
import lombok.extern.slf4j.Slf4j;

@Slf4j
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

    try {
      final String taskQueueForConnectionId = routerService.getTaskQueue(input.getConnectionId());

      return new RouteToSyncTaskQueueOutput(taskQueueForConnectionId);
    } catch (final IOException e) {
      log.warn("Encountered an error while attempting to route connection {} to a task queue: \n{}", input.getConnectionId(), e);
      throw new RetryableException(e);
    }
  }

}
