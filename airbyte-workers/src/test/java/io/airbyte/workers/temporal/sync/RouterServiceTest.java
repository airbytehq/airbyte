/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import static io.airbyte.workers.temporal.sync.RouterService.MVP_DATA_PLANE_TASK_QUEUE;
import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.workers.temporal.TemporalJobType;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link RouterService} class.
 */
class RouterServiceTest {

  @Test
  void testSelectionOfTaskQueueForDataPlane() {
    final UUID connectionId = UUID.randomUUID();
    final String connectionIdsForMvpDataPlane = connectionId.toString();
    final RouterService routerService = new RouterService();
    routerService.setConnectionIdsForMvpDataPlane(connectionIdsForMvpDataPlane);

    final String taskQueue = routerService.getTaskQueue(connectionId);
    assertEquals(MVP_DATA_PLANE_TASK_QUEUE, taskQueue);
  }

  @Test
  void testSelectionOfTaskQueueForNonMatchingConnectionId() {
    final UUID connectionId = UUID.randomUUID();
    final String connectionIdsForMvpDataPlane = "1,2,3,4,5";
    final RouterService routerService = new RouterService();
    routerService.setConnectionIdsForMvpDataPlane(connectionIdsForMvpDataPlane);

    final String taskQueue = routerService.getTaskQueue(connectionId);
    assertEquals(TemporalJobType.SYNC.name(), taskQueue);
  }

  @Test
  void testSelectionOfTaskQueueForNullConnectionId() {
    final String connectionIdsForMvpDataPlane = "1,2,3,4,5";
    final RouterService routerService = new RouterService();
    routerService.setConnectionIdsForMvpDataPlane(connectionIdsForMvpDataPlane);

    final String taskQueue = routerService.getTaskQueue(null);
    assertEquals(TemporalJobType.SYNC.name(), taskQueue);
  }

  @Test
  void testSelectionOfTaskQueueForBlankConnectionIdSet() {
    final UUID connectionId = UUID.randomUUID();
    final RouterService routerService = new RouterService();

    final String taskQueue = routerService.getTaskQueue(connectionId);
    assertEquals(TemporalJobType.SYNC.name(), taskQueue);
  }

}
