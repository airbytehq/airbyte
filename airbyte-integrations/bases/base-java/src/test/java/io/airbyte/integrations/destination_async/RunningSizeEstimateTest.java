/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class RunningSizeEstimateTest {

  private static final long SIZE_10MB = 10 * 1024 * 1024;
  private static final long SIZE_20MB = 20 * 1024 * 1024;
  private static final long SIZE_200MB = 200 * 1024 * 1024;
  private static final StreamDescriptor DESC1 = new StreamDescriptor().withName("test1");

  private static DestinationFlushFunction flusher;

  @BeforeEach
  void setup() {
    flusher = mock(DestinationFlushFunction.class);
    when(flusher.getOptimalBatchSizeBytes()).thenReturn(SIZE_200MB);
  }

  @Test
  void testEstimateZeroWorkers() {
    final RunningFlushWorkers runningFlushWorkers = mock(RunningFlushWorkers.class);
    when(runningFlushWorkers.getSizesOfRunningWorkerBatches(any())).thenReturn(Collections.emptyList());
    final DetectStreamToFlush detect = new DetectStreamToFlush(null, runningFlushWorkers, null, flusher);
    assertEquals(0, detect.estimateSizeOfRunningWorkers(DESC1, SIZE_10MB));
  }

  @Test
  void testEstimateWorkerWithBatch() {
    final RunningFlushWorkers runningFlushWorkers = mock(RunningFlushWorkers.class);
    when(runningFlushWorkers.getSizesOfRunningWorkerBatches(any())).thenReturn(List.of(Optional.of(SIZE_20MB)));
    final DetectStreamToFlush detect = new DetectStreamToFlush(null, runningFlushWorkers, null, flusher);
    assertEquals(SIZE_20MB, detect.estimateSizeOfRunningWorkers(DESC1, SIZE_10MB));
  }

  @Test
  void testEstimateWorkerWithoutBatchAndQueueLessThanOptimalSize() {
    final RunningFlushWorkers runningFlushWorkers = mock(RunningFlushWorkers.class);
    when(runningFlushWorkers.getSizesOfRunningWorkerBatches(any())).thenReturn(List.of(Optional.empty()));
    final DetectStreamToFlush detect = new DetectStreamToFlush(null, runningFlushWorkers, null, flusher);
    assertEquals(SIZE_10MB, detect.estimateSizeOfRunningWorkers(DESC1, SIZE_10MB));
  }

  @Test
  void testEstimateWorkerWithoutBatchAndQueueGreaterThanOptimalSize() {
    final RunningFlushWorkers runningFlushWorkers = mock(RunningFlushWorkers.class);
    when(runningFlushWorkers.getSizesOfRunningWorkerBatches(any())).thenReturn(List.of(Optional.empty()));
    final DetectStreamToFlush detect = new DetectStreamToFlush(null, runningFlushWorkers, null, flusher);
    assertEquals(SIZE_200MB, detect.estimateSizeOfRunningWorkers(DESC1, SIZE_200MB + 1));
  }

}
