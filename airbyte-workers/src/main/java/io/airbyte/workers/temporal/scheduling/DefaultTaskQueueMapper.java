/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.temporal.TemporalJobType;
import io.airbyte.commons.temporal.scheduling.TaskQueueMapper;
import io.airbyte.config.Geography;
import jakarta.inject.Singleton;
import java.util.Map;

@Singleton
public class DefaultTaskQueueMapper implements TaskQueueMapper {

  @VisibleForTesting
  static final String DEFAULT_SYNC_TASK_QUEUE = TemporalJobType.SYNC.name();

  // By default, map every Geography value to the default task queue.
  // To override this behavior, define a new TaskQueueMapper bean with the @Primary annotation.
  @VisibleForTesting
  static final Map<Geography, String> GEOGRAPHY_TASK_QUEUE_MAP = Map.of(
      Geography.AUTO, DEFAULT_SYNC_TASK_QUEUE,
      Geography.US, DEFAULT_SYNC_TASK_QUEUE,
      Geography.EU, DEFAULT_SYNC_TASK_QUEUE);

  @Override
  public String getTaskQueue(final Geography geography) {
    if (GEOGRAPHY_TASK_QUEUE_MAP.containsKey(geography)) {
      return GEOGRAPHY_TASK_QUEUE_MAP.get(geography);
    }

    throw new IllegalArgumentException(String.format("Unexpected geography %s", geography));
  }

}
