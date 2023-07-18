/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.integrations.destination_async.buffers.BufferDequeue;
import java.util.concurrent.atomic.AtomicBoolean;
import org.junit.jupiter.api.Test;

public class FlushThresholdTest {

  private static final long SIZE_10MB = 10 * 1024 * 1024;

  @Test
  void testBaseThreshold() {
    final AtomicBoolean isClosing = new AtomicBoolean(false);
    final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
    final DetectStreamToFlush detect = new DetectStreamToFlush(bufferDequeue, null, isClosing, null);
    assertEquals(SIZE_10MB, detect.computeQueueThreshold());
  }

  @Test
  void testClosingThreshold() {
    final AtomicBoolean isClosing = new AtomicBoolean(true);
    final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
    final DetectStreamToFlush detect = new DetectStreamToFlush(bufferDequeue, null, isClosing, null);
    assertEquals(0, detect.computeQueueThreshold());
  }

  @Test
  void testEagerFlushThresholdBelowThreshold() {
    final AtomicBoolean isClosing = new AtomicBoolean(false);
    final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
    when(bufferDequeue.getTotalGlobalQueueSizeBytes()).thenReturn(8L);
    when(bufferDequeue.getMaxQueueSizeBytes()).thenReturn(10L);
    final DetectStreamToFlush detect = new DetectStreamToFlush(bufferDequeue, null, isClosing, null);
    assertEquals(SIZE_10MB, detect.computeQueueThreshold());
  }

  @Test
  void testEagerFlushThresholdAboveThreshold() {
    final AtomicBoolean isClosing = new AtomicBoolean(false);
    final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
    when(bufferDequeue.getTotalGlobalQueueSizeBytes()).thenReturn(9L);
    when(bufferDequeue.getMaxQueueSizeBytes()).thenReturn(10L);
    final DetectStreamToFlush detect = new DetectStreamToFlush(bufferDequeue, null, isClosing, null);
    assertEquals(0, detect.computeQueueThreshold());
  }

}
