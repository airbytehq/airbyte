/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.integrations.destination_async.buffers.BufferDequeue;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.time.Instant;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.atomic.AtomicBoolean;
import org.junit.jupiter.api.Test;

class DetectStreamToFlushTest {

  private static final long SIZE_10MB = 10 * 1024 * 1024; // 10MB
  public static final StreamDescriptor DESC = new StreamDescriptor().withName("test");

  @Test
  void testBaseThreshold() {
    final AtomicBoolean isClosing = new AtomicBoolean(false);
    final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
    final DetectStreamToFlush detectStreamToFlush = new DetectStreamToFlush(bufferDequeue, null, isClosing);
    assertEquals(SIZE_10MB, detectStreamToFlush.computeQueueThreshold());
  }

  @Test
  void testClosingThreshold() {
    final AtomicBoolean isClosing = new AtomicBoolean(true);
    final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
    final DetectStreamToFlush detectStreamToFlush = new DetectStreamToFlush(bufferDequeue, null, isClosing);
    assertEquals(0, detectStreamToFlush.computeQueueThreshold());
  }

  @Test
  void testEagerFlushThresholdBelowThreshold() {
    final AtomicBoolean isClosing = new AtomicBoolean(false);
    final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
    when(bufferDequeue.getTotalGlobalQueueSizeBytes()).thenReturn(8L);
    when(bufferDequeue.getTotalGlobalQueueSizeBytes()).thenReturn(10L);
    final DetectStreamToFlush detectStreamToFlush = new DetectStreamToFlush(bufferDequeue, null, isClosing);
    assertEquals(0, detectStreamToFlush.computeQueueThreshold());
  }

  @Test
  void testEagerFlushThresholdAboveThreshold() {
    final AtomicBoolean isClosing = new AtomicBoolean(false);
    final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
    when(bufferDequeue.getTotalGlobalQueueSizeBytes()).thenReturn(9L);
    when(bufferDequeue.getTotalGlobalQueueSizeBytes()).thenReturn(10L);
    final DetectStreamToFlush detectStreamToFlush = new DetectStreamToFlush(bufferDequeue, null, isClosing);
    assertEquals(0, detectStreamToFlush.computeQueueThreshold());
  }

  @Test
  void testGetNextSkipsEmptyStreams() {
    final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
    when(bufferDequeue.getBufferedStreams()).thenReturn(Set.of(DESC));
    when(bufferDequeue.getQueueSizeBytes(DESC)).thenReturn(Optional.of(0L));
    final RunningFlushWorkers runningFlushWorkers = mock(RunningFlushWorkers.class);
    when(runningFlushWorkers.getNumFlushWorkers(any())).thenReturn(0);
    final DetectStreamToFlush detectStreamToFlush = new DetectStreamToFlush(bufferDequeue, runningFlushWorkers, new AtomicBoolean(false));
    assertEquals(Optional.empty(), detectStreamToFlush.getNextStreamToFlush(0));
  }

  @Test
  void testGetNextPicksUpOnSizeTrigger() {
    final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
    when(bufferDequeue.getBufferedStreams()).thenReturn(Set.of(DESC));
    when(bufferDequeue.getQueueSizeBytes(DESC)).thenReturn(Optional.of(1L));
    final RunningFlushWorkers runningFlushWorkers = mock(RunningFlushWorkers.class);
    when(runningFlushWorkers.getNumFlushWorkers(any())).thenReturn(0);
    final DetectStreamToFlush detectStreamToFlush = new DetectStreamToFlush(bufferDequeue, runningFlushWorkers, new AtomicBoolean(false));
    // if below threshold, triggers
    assertEquals(Optional.of(DESC), detectStreamToFlush.getNextStreamToFlush(0));
    // if above threshold, no trigger
    assertEquals(Optional.empty(), detectStreamToFlush.getNextStreamToFlush(1));
  }

  @Test
  void testGetNextRespectsHigherThresholdWhenDescAlreadyRunning() {
    final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
    when(bufferDequeue.getBufferedStreams()).thenReturn(Set.of(DESC));
    when(bufferDequeue.getQueueSizeBytes(DESC)).thenReturn(Optional.of(1L));
    final RunningFlushWorkers runningFlushWorkers = mock(RunningFlushWorkers.class);
    when(runningFlushWorkers.getNumFlushWorkers(any())).thenReturn(1);
    final DetectStreamToFlush detectStreamToFlush = new DetectStreamToFlush(bufferDequeue, runningFlushWorkers, new AtomicBoolean(false));
    assertEquals(Optional.empty(), detectStreamToFlush.getNextStreamToFlush(0));
  }

  @Test
  void testGetNextPicksUpOnTimeTrigger() {
    final Instant now = Instant.now();
    final Instant fiveMinAgo = now.minusSeconds(60 * 5);
    final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
    when(bufferDequeue.getBufferedStreams()).thenReturn(Set.of(DESC));
    when(bufferDequeue.getQueueSizeBytes(DESC)).thenReturn(Optional.of(1L));
    when(bufferDequeue.getTimeOfLastRecord(DESC))
        .thenReturn(Optional.empty())
        .thenReturn(Optional.of(now))
        .thenReturn(Optional.of(fiveMinAgo));
    final RunningFlushWorkers runningFlushWorkers = mock(RunningFlushWorkers.class);
    when(runningFlushWorkers.getNumFlushWorkers(any())).thenReturn(1);
    final DetectStreamToFlush detectStreamToFlush = new DetectStreamToFlush(bufferDequeue, runningFlushWorkers, new AtomicBoolean(false));
    assertEquals(Optional.empty(), detectStreamToFlush.getNextStreamToFlush(0));
    assertEquals(Optional.empty(), detectStreamToFlush.getNextStreamToFlush(0));
    assertEquals(Optional.of(DESC), detectStreamToFlush.getNextStreamToFlush(0));
  }

}
