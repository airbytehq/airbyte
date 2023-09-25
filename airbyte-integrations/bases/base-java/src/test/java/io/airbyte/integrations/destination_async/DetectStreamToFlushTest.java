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
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.atomic.AtomicBoolean;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DetectStreamToFlushTest {

  public static final Instant NOW = Instant.now();
  public static final Instant FIVE_MIN_AGO = NOW.minusSeconds(60 * 5);
  private static final long SIZE_10MB = 10 * 1024 * 1024;
  private static final long SIZE_200MB = 200 * 1024 * 1024;

  private static final StreamDescriptor DESC1 = new StreamDescriptor().withName("test1");

  private static DestinationFlushFunction flusher;

  @BeforeEach
  void setup() {
    flusher = mock(DestinationFlushFunction.class);
    when(flusher.getOptimalBatchSizeBytes()).thenReturn(SIZE_200MB);
  }

  @Test
  void testGetNextSkipsEmptyStreams() {
    final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
    when(bufferDequeue.getBufferedStreams()).thenReturn(Set.of(DESC1));
    when(bufferDequeue.getQueueSizeBytes(DESC1)).thenReturn(Optional.of(0L));
    final RunningFlushWorkers runningFlushWorkers = mock(RunningFlushWorkers.class);
    final DetectStreamToFlush detect = new DetectStreamToFlush(bufferDequeue, runningFlushWorkers, new AtomicBoolean(false), flusher);
    assertEquals(Optional.empty(), detect.getNextStreamToFlush(0));
  }

  @Test
  void testGetNextPicksUpOnSizeTrigger() {
    final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
    when(bufferDequeue.getBufferedStreams()).thenReturn(Set.of(DESC1));
    when(bufferDequeue.getQueueSizeBytes(DESC1)).thenReturn(Optional.of(1L));
    final RunningFlushWorkers runningFlushWorkers = mock(RunningFlushWorkers.class);
    final DetectStreamToFlush detect = new DetectStreamToFlush(bufferDequeue, runningFlushWorkers, new AtomicBoolean(false), flusher);
    // if above threshold, triggers
    assertEquals(Optional.of(DESC1), detect.getNextStreamToFlush(0));
    // if below threshold, no trigger
    assertEquals(Optional.empty(), detect.getNextStreamToFlush(1));
  }

  @Test
  void testGetNextAccountsForAlreadyRunningWorkers() {
    final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
    when(bufferDequeue.getBufferedStreams()).thenReturn(Set.of(DESC1));
    when(bufferDequeue.getQueueSizeBytes(DESC1)).thenReturn(Optional.of(1L));
    final RunningFlushWorkers runningFlushWorkers = mock(RunningFlushWorkers.class);
    when(runningFlushWorkers.getSizesOfRunningWorkerBatches(any())).thenReturn(List.of(Optional.of(SIZE_10MB)));
    final DetectStreamToFlush detect = new DetectStreamToFlush(bufferDequeue, runningFlushWorkers, new AtomicBoolean(false), flusher);
    assertEquals(Optional.empty(), detect.getNextStreamToFlush(0));
  }

  @Test
  void testGetNextPicksUpOnTimeTrigger() {
    final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
    when(bufferDequeue.getBufferedStreams()).thenReturn(Set.of(DESC1));
    when(bufferDequeue.getQueueSizeBytes(DESC1)).thenReturn(Optional.of(1L));
    when(bufferDequeue.getTimeOfLastRecord(DESC1))
        // because we eagerly load values and later access them again
        // double the mocks for correctness; two calls here equals one test case.
        .thenReturn(Optional.empty())
        .thenReturn(Optional.empty())
        .thenReturn(Optional.of(NOW))
        .thenReturn(Optional.of(NOW))
        .thenReturn(Optional.of(FIVE_MIN_AGO))
        .thenReturn(Optional.of(FIVE_MIN_AGO));

    final RunningFlushWorkers runningFlushWorkers = mock(RunningFlushWorkers.class);
    when(runningFlushWorkers.getSizesOfRunningWorkerBatches(any())).thenReturn(List.of(Optional.of(SIZE_10MB)));
    final DetectStreamToFlush detect = new DetectStreamToFlush(bufferDequeue, runningFlushWorkers, new AtomicBoolean(false), flusher);
    assertEquals(Optional.empty(), detect.getNextStreamToFlush(0));
    assertEquals(Optional.empty(), detect.getNextStreamToFlush(0));
    assertEquals(Optional.of(DESC1), detect.getNextStreamToFlush(0));
  }

}
