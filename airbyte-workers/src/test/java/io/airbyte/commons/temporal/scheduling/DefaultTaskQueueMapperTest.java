/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal.scheduling;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.temporal.TemporalJobType;
import io.airbyte.config.Geography;
import org.junit.jupiter.api.Test;

class DefaultTaskQueueMapperTest {

  @Test
  void testGetSyncTaskQueue() {
    // By default, every Geography should map to the default SYNC task queue
    final TaskQueueMapper mapper = new DefaultTaskQueueMapper();

    assertEquals(DefaultTaskQueueMapper.DEFAULT_SYNC_TASK_QUEUE, mapper.getTaskQueue(Geography.AUTO, TemporalJobType.SYNC));
    assertEquals(DefaultTaskQueueMapper.DEFAULT_SYNC_TASK_QUEUE, mapper.getTaskQueue(Geography.US, TemporalJobType.SYNC));
    assertEquals(DefaultTaskQueueMapper.DEFAULT_SYNC_TASK_QUEUE, mapper.getTaskQueue(Geography.EU, TemporalJobType.SYNC));
  }

  @Test
  void testGetCheckTaskQueue() {
    final TaskQueueMapper mapper = new DefaultTaskQueueMapper();

    assertEquals(DefaultTaskQueueMapper.DEFAULT_CHECK_TASK_QUEUE, mapper.getTaskQueue(Geography.AUTO, TemporalJobType.CHECK_CONNECTION));
    assertEquals(DefaultTaskQueueMapper.DEFAULT_CHECK_TASK_QUEUE, mapper.getTaskQueue(Geography.US, TemporalJobType.CHECK_CONNECTION));
    assertEquals(DefaultTaskQueueMapper.DEFAULT_CHECK_TASK_QUEUE, mapper.getTaskQueue(Geography.EU, TemporalJobType.CHECK_CONNECTION));
  }

  @Test
  void testGetDiscoverTaskQueue() {
    final TaskQueueMapper mapper = new DefaultTaskQueueMapper();

    assertEquals(DefaultTaskQueueMapper.DEFAULT_DISCOVER_TASK_QUEUE, mapper.getTaskQueue(Geography.AUTO, TemporalJobType.DISCOVER_SCHEMA));
    assertEquals(DefaultTaskQueueMapper.DEFAULT_DISCOVER_TASK_QUEUE, mapper.getTaskQueue(Geography.US, TemporalJobType.DISCOVER_SCHEMA));
    assertEquals(DefaultTaskQueueMapper.DEFAULT_DISCOVER_TASK_QUEUE, mapper.getTaskQueue(Geography.EU, TemporalJobType.DISCOVER_SCHEMA));
  }

}
