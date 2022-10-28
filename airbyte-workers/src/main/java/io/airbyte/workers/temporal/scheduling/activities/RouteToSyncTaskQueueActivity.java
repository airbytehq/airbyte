/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@ActivityInterface
public interface RouteToSyncTaskQueueActivity {

  @ActivityMethod
  RouteToSyncTaskQueueOutput route(RouteToSyncTaskQueueInput input);

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class RouteToSyncTaskQueueInput {

    private UUID connectionId;

  }

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class RouteToSyncTaskQueueOutput {

    private String taskQueue;

  }

}
