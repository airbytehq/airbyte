/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal.scheduling;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.temporal.TemporalJobType;
import io.airbyte.config.Geography;
import jakarta.inject.Singleton;

@Singleton
public class DefaultTaskQueueMapper implements TaskQueueMapper {

  @VisibleForTesting
  static final String DEFAULT_SYNC_TASK_QUEUE = TemporalJobType.SYNC.name();
  @VisibleForTesting
  static final String DEFAULT_CHECK_TASK_QUEUE = TemporalJobType.CHECK_CONNECTION.name();
  @VisibleForTesting
  static final String DEFAULT_DISCOVER_TASK_QUEUE = TemporalJobType.DISCOVER_SCHEMA.name();

  // By default, map every Geography value to the default task queue.
  // To override this behavior, define a new TaskQueueMapper bean with the @Primary annotation.
  @Override
  public String getTaskQueue(final Geography geography, final TemporalJobType jobType) {
    switch (jobType) {
      case CHECK_CONNECTION:
        return DEFAULT_CHECK_TASK_QUEUE;
      case DISCOVER_SCHEMA:
        return DEFAULT_DISCOVER_TASK_QUEUE;
      case SYNC:
        return DEFAULT_SYNC_TASK_QUEUE;
      default:
        throw new IllegalArgumentException(String.format("Unexpected jobType %s", jobType));
    }
  }

}
