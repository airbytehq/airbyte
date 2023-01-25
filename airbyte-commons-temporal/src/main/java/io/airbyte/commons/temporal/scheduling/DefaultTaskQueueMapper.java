/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal.scheduling;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.temporal.TemporalJobType;
import io.airbyte.config.Geography;
import jakarta.inject.Singleton;
import java.util.Map;

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
  @VisibleForTesting
  static final Map<Geography, String> GEOGRAPHY_SYNC_TASK_QUEUE_MAP = Map.of(
      Geography.AUTO, DEFAULT_SYNC_TASK_QUEUE,
      Geography.US, DEFAULT_SYNC_TASK_QUEUE,
      Geography.EU, DEFAULT_SYNC_TASK_QUEUE);

  @VisibleForTesting
  static final Map<Geography, String> GEOGRAPHY_CHECK_TASK_QUEUE_MAP = Map.of(
      Geography.AUTO, DEFAULT_CHECK_TASK_QUEUE,
      Geography.US, DEFAULT_CHECK_TASK_QUEUE,
      Geography.EU, DEFAULT_CHECK_TASK_QUEUE);

  @VisibleForTesting
  static final Map<Geography, String> GEOGRAPHY_DISCOVER_TASK_QUEUE_MAP = Map.of(
      Geography.AUTO, DEFAULT_DISCOVER_TASK_QUEUE,
      Geography.US, DEFAULT_DISCOVER_TASK_QUEUE,
      Geography.EU, DEFAULT_DISCOVER_TASK_QUEUE);

  @Override
  public String getTaskQueue(final Geography geography) {
    if (GEOGRAPHY_SYNC_TASK_QUEUE_MAP.containsKey(geography)) {
      return GEOGRAPHY_SYNC_TASK_QUEUE_MAP.get(geography);
    }

    throw new IllegalArgumentException(String.format("Unexpected geography %s", geography));
  }

  /**
   * @param geography
   * @return
   */
  @Override
  public String getDiscoverTaskQueue(Geography geography) {
    if (GEOGRAPHY_DISCOVER_TASK_QUEUE_MAP.containsKey(geography)) {
      return GEOGRAPHY_DISCOVER_TASK_QUEUE_MAP.get(geography);
    }

    throw new IllegalArgumentException(String.format("Unexpected geography %s", geography));
  }

  /**
   * @param geography
   * @return
   */
  @Override
  public String getCheckTaskQueue(Geography geography) {
    if (GEOGRAPHY_CHECK_TASK_QUEUE_MAP.containsKey(geography)) {
      return GEOGRAPHY_CHECK_TASK_QUEUE_MAP.get(geography);
    }

    throw new IllegalArgumentException(String.format("Unexpected geography %s", geography));
  }

}
