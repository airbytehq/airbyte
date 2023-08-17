/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class RunningFlushWorkersTest {

  private static final long SIZE_10MB = 10 * 1024 * 1024;

  private static final UUID FLUSH_WORKER_ID1 = UUID.randomUUID();
  private static final UUID FLUSH_WORKER_ID2 = UUID.randomUUID();
  private static final StreamDescriptor STREAM1 = new StreamDescriptor().withNamespace("namespace1").withName("stream1");
  private static final StreamDescriptor STREAM2 = new StreamDescriptor().withNamespace("namespace2").withName("stream2");

  private RunningFlushWorkers runningFlushWorkers;

  @BeforeEach
  void setup() {
    runningFlushWorkers = new RunningFlushWorkers();
  }

  @Test
  void testTrackFlushWorker() {
    assertThat(runningFlushWorkers.getSizesOfRunningWorkerBatches(STREAM1).size()).isEqualTo(0);
    runningFlushWorkers.trackFlushWorker(STREAM1, FLUSH_WORKER_ID1);
    assertThat(runningFlushWorkers.getSizesOfRunningWorkerBatches(STREAM1).size()).isEqualTo(1);
    runningFlushWorkers.trackFlushWorker(STREAM1, FLUSH_WORKER_ID2);
    runningFlushWorkers.trackFlushWorker(STREAM2, FLUSH_WORKER_ID1);
    assertThat(runningFlushWorkers.getSizesOfRunningWorkerBatches(STREAM1).size()).isEqualTo(2);
  }

  @Test
  void testCompleteFlushWorker() {
    runningFlushWorkers.trackFlushWorker(STREAM1, FLUSH_WORKER_ID1);
    runningFlushWorkers.trackFlushWorker(STREAM1, FLUSH_WORKER_ID2);
    runningFlushWorkers.completeFlushWorker(STREAM1, FLUSH_WORKER_ID1);
    assertThat(runningFlushWorkers.getSizesOfRunningWorkerBatches(STREAM1).size()).isEqualTo(1);
    runningFlushWorkers.completeFlushWorker(STREAM1, FLUSH_WORKER_ID2);
    assertThat(runningFlushWorkers.getSizesOfRunningWorkerBatches(STREAM1).size()).isEqualTo(0);
  }

  @Test
  void testCompleteFlushWorkerWithoutTrackThrowsException() {
    assertThatThrownBy(() -> runningFlushWorkers.completeFlushWorker(STREAM1, FLUSH_WORKER_ID1))
        .isInstanceOf(IllegalStateException.class)
        .hasMessageContaining("Cannot complete flush worker for stream that has not started.");
  }

  @Test
  void testMultipleStreams() {
    runningFlushWorkers.trackFlushWorker(STREAM1, FLUSH_WORKER_ID1);
    runningFlushWorkers.trackFlushWorker(STREAM2, FLUSH_WORKER_ID1);
    assertThat(runningFlushWorkers.getSizesOfRunningWorkerBatches(STREAM1).size()).isEqualTo(1);
    assertThat(runningFlushWorkers.getSizesOfRunningWorkerBatches(STREAM2).size()).isEqualTo(1);
  }

  @Test
  void testGetSizesOfRunningWorkerBatches() {
    runningFlushWorkers.trackFlushWorker(STREAM1, FLUSH_WORKER_ID1);
    runningFlushWorkers.trackFlushWorker(STREAM1, FLUSH_WORKER_ID2);
    runningFlushWorkers.trackFlushWorker(STREAM2, FLUSH_WORKER_ID1);
    assertEquals(List.of(Optional.empty(), Optional.empty()),
        runningFlushWorkers.getSizesOfRunningWorkerBatches(STREAM1));
    assertEquals(List.of(Optional.empty()), runningFlushWorkers.getSizesOfRunningWorkerBatches(STREAM2));
    assertThrows(IllegalStateException.class, () -> runningFlushWorkers.registerBatchSize(STREAM2, FLUSH_WORKER_ID2, SIZE_10MB));
    runningFlushWorkers.registerBatchSize(STREAM1, FLUSH_WORKER_ID1, SIZE_10MB);
    runningFlushWorkers.registerBatchSize(STREAM1, FLUSH_WORKER_ID2, SIZE_10MB);
    runningFlushWorkers.registerBatchSize(STREAM2, FLUSH_WORKER_ID1, SIZE_10MB);
    assertEquals(List.of(Optional.of(SIZE_10MB), Optional.of(SIZE_10MB)), runningFlushWorkers.getSizesOfRunningWorkerBatches(STREAM1));
    assertEquals(List.of(Optional.of(SIZE_10MB)), runningFlushWorkers.getSizesOfRunningWorkerBatches(STREAM2));
  }

}
