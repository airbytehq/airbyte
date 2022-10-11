/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.helper;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.temporal.scheduling.GeographyMapper;
import io.airbyte.config.Geography;
import java.util.Arrays;
import java.util.Set;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

class DefaultGeographyMapperTest {

  @Test
  void testGetTaskQueue() {
    // By default, every Geography should map to the default SYNC task queue
    final GeographyMapper mapper = new DefaultGeographyMapper();

    assertEquals(DefaultGeographyMapper.DEFAULT_SYNC_TASK_QUEUE, mapper.getTaskQueue(Geography.AUTO));
    assertEquals(DefaultGeographyMapper.DEFAULT_SYNC_TASK_QUEUE, mapper.getTaskQueue(Geography.US));
    assertEquals(DefaultGeographyMapper.DEFAULT_SYNC_TASK_QUEUE, mapper.getTaskQueue(Geography.EU));
  }

  /**
   * If this test fails, it likely means that a new value was added to the {@link Geography} enum. A
   * new entry must be added to {@link DefaultGeographyMapper#GEOGRAPHY_TASK_QUEUE_MAP} to get this
   * test to pass.
   */
  @Test
  void testAllGeographiesHaveAMapping() {
    final Set<Geography> allGeographies = Arrays.stream(Geography.values()).collect(Collectors.toSet());
    final Set<Geography> mappedGeographies = DefaultGeographyMapper.GEOGRAPHY_TASK_QUEUE_MAP.keySet();

    assertEquals(allGeographies, mappedGeographies);
  }

}
