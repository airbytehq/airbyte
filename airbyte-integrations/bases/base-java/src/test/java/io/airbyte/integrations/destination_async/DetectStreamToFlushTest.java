/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination_async.buffers.BufferDequeue;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.time.Instant;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.atomic.AtomicBoolean;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

class DetectStreamToFlushTest {

  public static final Instant NOW = Instant.now();
  public static final Instant FIVE_MIN_AGO = NOW.minusSeconds(60 * 5);
  private static final long SIZE_10MB = 10 * 1024 * 1024; // 10MB
  private static final StreamDescriptor DESC1 = new StreamDescriptor().withName("test1");
  private static final StreamDescriptor DESC2 = new StreamDescriptor().withName("test2");
  private static final Set<StreamDescriptor> DESCS = Set.of(DESC1, DESC2);

  @Nested
  class Threshold {

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
      when(bufferDequeue.getMaxQueueSizeBytes()).thenReturn(10L);
      final DetectStreamToFlush detectStreamToFlush = new DetectStreamToFlush(bufferDequeue, null, isClosing);
      assertEquals(SIZE_10MB, detectStreamToFlush.computeQueueThreshold());
    }

    @Test
    void testEagerFlushThresholdAboveThreshold() {
      final AtomicBoolean isClosing = new AtomicBoolean(false);
      final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
      when(bufferDequeue.getTotalGlobalQueueSizeBytes()).thenReturn(9L);
      when(bufferDequeue.getMaxQueueSizeBytes()).thenReturn(10L);
      final DetectStreamToFlush detectStreamToFlush = new DetectStreamToFlush(bufferDequeue, null, isClosing);
      assertEquals(0, detectStreamToFlush.computeQueueThreshold());
    }

  }

  @Nested
  class GetNextStreamToFlush {

    @Test
    void testGetNextSkipsEmptyStreams() {
      final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
      when(bufferDequeue.getBufferedStreams()).thenReturn(Set.of(DESC1));
      when(bufferDequeue.getQueueSizeBytes(DESC1)).thenReturn(Optional.of(0L));
      final RunningFlushWorkers runningFlushWorkers = mock(RunningFlushWorkers.class);
      when(runningFlushWorkers.getNumFlushWorkers(any())).thenReturn(0);
      final DetectStreamToFlush detectStreamToFlush = new DetectStreamToFlush(bufferDequeue, runningFlushWorkers, new AtomicBoolean(false));
      assertEquals(Optional.empty(), detectStreamToFlush.getNextStreamToFlush(0));
    }

    @Test
    void testGetNextPicksUpOnSizeTrigger() {
      final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
      when(bufferDequeue.getBufferedStreams()).thenReturn(Set.of(DESC1));
      when(bufferDequeue.getQueueSizeBytes(DESC1)).thenReturn(Optional.of(1L));
      final RunningFlushWorkers runningFlushWorkers = mock(RunningFlushWorkers.class);
      when(runningFlushWorkers.getNumFlushWorkers(any())).thenReturn(0);
      final DetectStreamToFlush detectStreamToFlush = new DetectStreamToFlush(bufferDequeue, runningFlushWorkers, new AtomicBoolean(false));
      // if below threshold, triggers
      assertEquals(Optional.of(DESC1), detectStreamToFlush.getNextStreamToFlush(0));
      // if above threshold, no trigger
      assertEquals(Optional.empty(), detectStreamToFlush.getNextStreamToFlush(1));
    }

    @Test
    void testGetNextRespectsHigherThresholdWhenDescAlreadyRunning() {
      final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
      when(bufferDequeue.getBufferedStreams()).thenReturn(Set.of(DESC1));
      when(bufferDequeue.getQueueSizeBytes(DESC1)).thenReturn(Optional.of(1L));
      final RunningFlushWorkers runningFlushWorkers = mock(RunningFlushWorkers.class);
      when(runningFlushWorkers.getNumFlushWorkers(any())).thenReturn(1);
      final DetectStreamToFlush detectStreamToFlush = new DetectStreamToFlush(bufferDequeue, runningFlushWorkers, new AtomicBoolean(false));
      assertEquals(Optional.empty(), detectStreamToFlush.getNextStreamToFlush(0));
    }

    @Test
    void testGetNextPicksUpOnTimeTrigger() {
      final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
      when(bufferDequeue.getBufferedStreams()).thenReturn(Set.of(DESC1));
      when(bufferDequeue.getQueueSizeBytes(DESC1)).thenReturn(Optional.of(1L));
      when(bufferDequeue.getTimeOfLastRecord(DESC1))
          .thenReturn(Optional.empty())
          .thenReturn(Optional.of(NOW))
          .thenReturn(Optional.of(FIVE_MIN_AGO));
      final RunningFlushWorkers runningFlushWorkers = mock(RunningFlushWorkers.class);
      when(runningFlushWorkers.getNumFlushWorkers(any())).thenReturn(1);
      final DetectStreamToFlush detectStreamToFlush = new DetectStreamToFlush(bufferDequeue, runningFlushWorkers, new AtomicBoolean(false));
      assertEquals(Optional.empty(), detectStreamToFlush.getNextStreamToFlush(0));
      assertEquals(Optional.empty(), detectStreamToFlush.getNextStreamToFlush(0));
      assertEquals(Optional.of(DESC1), detectStreamToFlush.getNextStreamToFlush(0));
    }

  }

  @Nested
  class StreamPriorityOrdering {

    @Test
    void testOrderByPrioritySize() {
      final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
      when(bufferDequeue.getQueueSizeBytes(DESC1)).thenReturn(Optional.of(1L)).thenReturn(Optional.of(0L));
      when(bufferDequeue.getQueueSizeBytes(DESC2)).thenReturn(Optional.of(0L)).thenReturn(Optional.of(1L));
      final DetectStreamToFlush detectStreamToFlush = new DetectStreamToFlush(bufferDequeue, null, new AtomicBoolean(false));

      assertEquals(List.of(DESC1, DESC2), detectStreamToFlush.orderStreamsByPriority(DESCS));
      assertEquals(List.of(DESC2, DESC1), detectStreamToFlush.orderStreamsByPriority(DESCS));
    }

    @Test
    void testOrderByPrioritySecondarySortByTime() {
      final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
      when(bufferDequeue.getQueueSizeBytes(any())).thenReturn(Optional.of(0L));
      when(bufferDequeue.getTimeOfLastRecord(DESC1)).thenReturn(Optional.of(FIVE_MIN_AGO)).thenReturn(Optional.of(NOW));
      when(bufferDequeue.getTimeOfLastRecord(DESC2)).thenReturn(Optional.of(NOW)).thenReturn(Optional.of(FIVE_MIN_AGO));
      final DetectStreamToFlush detectStreamToFlush = new DetectStreamToFlush(bufferDequeue, null, new AtomicBoolean(false));
      assertEquals(List.of(DESC1, DESC2), detectStreamToFlush.orderStreamsByPriority(DESCS));
      assertEquals(List.of(DESC2, DESC1), detectStreamToFlush.orderStreamsByPriority(DESCS));
    }

    @Test
    void testOrderByPriorityTertiarySortByName() {
      final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
      when(bufferDequeue.getQueueSizeBytes(any())).thenReturn(Optional.of(0L));
      when(bufferDequeue.getTimeOfLastRecord(any())).thenReturn(Optional.of(NOW));
      final DetectStreamToFlush detectStreamToFlush = new DetectStreamToFlush(bufferDequeue, null, new AtomicBoolean(false));
      final List<StreamDescriptor> descs = List.of(Jsons.clone(DESC1), Jsons.clone(DESC2));
      assertEquals(List.of(descs.get(0), descs.get(1)), detectStreamToFlush.orderStreamsByPriority(new HashSet<>(descs)));
      descs.get(0).setName("test3");
      assertEquals(List.of(descs.get(1), descs.get(0)), detectStreamToFlush.orderStreamsByPriority(new HashSet<>(descs)));
    }

  }

}
